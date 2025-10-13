"""
Improved Service Bus replication function following best practices.
This module implements Service Bus message replication.
"""

import logging
from typing import Any
import azure.functions as func
from azure.core.exceptions import (
    AzureError,
    ClientAuthenticationError,
    HttpResponseError,
    ResourceNotFoundError,
    ServiceRequestError,
)
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus.management import ServiceBusAdministrationClient
from azure.servicebus.exceptions import ServiceBusError
from pydantic import ValidationError as PydanticValidationError

from .config import ReplicationConfig
from .constants import ALERT_SEVERITY_CRITICAL, ALERT_SEVERITY_HIGH
from .error_handlers import (
    handle_authentication_error,
    handle_azure_error,
    handle_http_response_error,
    handle_resource_not_found_error,
    handle_service_bus_error,
    handle_service_request_error,
    handle_unexpected_error,
)
from .exceptions import ConfigError, ValidationError
from .logging_utils import configure_logger, log_replication_start, log_replication_success
from .message_utils import create_replicated_message, generate_correlation_id
from .retry_utils import exponential_backoff_retry

# Configure global logger
app_logger = configure_logger()


def configure_application_logging(config: ReplicationConfig) -> logging.Logger:
    return configure_logger(config)


def load_and_validate_config() -> ReplicationConfig:
    """Load and validate replication configuration."""
    try:
        config = ReplicationConfig()
        app_logger.info("Replication configuration loaded successfully",
                        extra={"replication_type": config.replication_type})
        return config
    except PydanticValidationError as e:
        raise ConfigError(f"Configuration validation failed: {e}") from e
    except Exception as e:
        raise ConfigError(f"Unexpected error loading configuration: {e}") from e


def send_message_to_destination(dest_conn: str, dest_topic: str,
                                message: ServiceBusMessage, correlation_id: str) -> None:
    """Send a message to the destination topic."""
    app_logger.debug("Sending message to destination topic",
                     extra={"correlation_id": correlation_id,
                            "destination_topic": dest_topic})
    with ServiceBusClient.from_connection_string(dest_conn) as client:
        with client.get_topic_sender(topic_name=dest_topic) as sender:
            sender.send_messages(message)


def _create_retry_send_function(source_message: func.ServiceBusMessage,
                                dest_conn: str, dest_topic: str,
                                ttl_seconds: int, direction: str,
                                correlation_id: str, retry_decorator: Any) -> Any:
    """Create retry-enabled send function."""
    @retry_decorator
    def send_with_retry(**kwargs: Any) -> None:
        replicated = create_replicated_message(
            source_message=source_message,
            correlation_id=correlation_id,
            ttl_seconds=ttl_seconds,
        )
        send_message_to_destination(dest_conn, dest_topic, replicated, correlation_id)
        _log_successful_replication(source_message, replicated, correlation_id,
                                    direction, dest_topic)
    return send_with_retry


def _log_successful_replication(source_message: func.ServiceBusMessage,
                                replicated_message: ServiceBusMessage,
                                correlation_id: str, direction: str,
                                dest_topic: str) -> None:
    """Log successful replication."""
    src_body = source_message.get_body()
    log_replication_success(
        logger=app_logger,
        correlation_id=correlation_id,
        direction=direction,
        destination_queue=dest_topic,
        original_message_id=source_message.message_id,
        replicated_message_id=getattr(replicated_message, "message_id", "unknown"),
        body_type=type(src_body).__name__,
        content_type=getattr(replicated_message, "content_type", "unknown"),
        body_size_bytes=len(str(getattr(replicated_message, "body", ""))),
    )


def _handle_replication_exceptions(send_fn: Any, correlation_id: str,
                                   direction: str, dest_topic: str,
                                   logger: logging.Logger) -> None:
    """Run send with full Azure error handling."""
    try:
        send_fn(correlation_id=correlation_id)
    except ClientAuthenticationError as e:
        handle_authentication_error(e, correlation_id, direction, dest_topic, logger)
    except ResourceNotFoundError as e:
        handle_resource_not_found_error(e, correlation_id, direction, dest_topic, logger)
    except ServiceRequestError as e:
        handle_service_request_error(e, correlation_id, direction, dest_topic, logger)
    except ServiceBusError as e:
        handle_service_bus_error(e, correlation_id, direction, dest_topic, logger)
    except HttpResponseError as e:
        handle_http_response_error(e, correlation_id, direction, dest_topic, logger)
    except AzureError as e:
        handle_azure_error(e, correlation_id, direction, dest_topic, logger)
    except Exception as e:
        handle_unexpected_error(e, correlation_id, direction, dest_topic, logger)


def replicate_message_to_destination(source_message: func.ServiceBusMessage,
                                     dest_conn: str, dest_topic: str,
                                     ttl_seconds: int, direction: str,
                                     max_retry: int, base_delay: float) -> None:
    """Replicate one message to destination topic."""
    corr_id = generate_correlation_id(source_message)
    log_replication_start(app_logger, corr_id, direction, dest_topic,
                          source_message.message_id, ttl_seconds)
    retry = exponential_backoff_retry(max_attempts=max_retry,
                                      base_delay=base_delay,
                                      logger=app_logger)
    send_fn = _create_retry_send_function(source_message, dest_conn,
                                          dest_topic, ttl_seconds,
                                          direction, corr_id, retry)
    _handle_replication_exceptions(send_fn, corr_id, direction, dest_topic, app_logger)


def orchestrate_replication(source_message: func.ServiceBusMessage,
                             config: ReplicationConfig) -> None:
    """Coordinate one message replication."""
    dest_conn, dest_topic, direction = config.get_destination_config()
    replicate_message_to_destination(source_message, dest_conn, dest_topic,
                                     config.ttl_seconds, direction,
                                     config.retry_config.max_attempts,
                                     config.retry_config.base_delay)


def get_all_topics_and_subscriptions(conn_str: str) -> dict[str, list[str]]:
    """Return mapping of topic -> [subscriptions]."""
    admin = ServiceBusAdministrationClient.from_connection_string(conn_str)
    mapping: dict[str, list[str]] = {}
    for topic in admin.list_topics():
        subs = [s.name for s in admin.list_subscriptions(topic.name)]
        mapping[topic.name] = subs
    return mapping


def main(timer: func.TimerRequest) -> None:
    """Timer-triggered replication orchestrator."""
    app_logger.info("Replication cron cycle started.")
    try:
        config = load_and_validate_config()
        logger = configure_application_logging(config)
        logger.info("Replication cron job running...")

        # Discover topics and subscriptions dynamically
        topic_map = get_all_topics_and_subscriptions(config.primary_conn_str)
        logger.info(f"Discovered topics: {list(topic_map.keys())}")

        with ServiceBusClient.from_connection_string(config.primary_conn_str) as client:
            for topic, subs in topic_map.items():
                for sub in subs:
                    logger.info(f"Processing {topic}/{sub}")
                    with client.get_subscription_receiver(topic, sub, max_wait_time=5) as receiver:
                        messages = receiver.receive_messages(max_message_count=100)
                        for msg in messages:
                            orchestrate_replication(msg, config)
                            receiver.complete_message(msg)

        logger.info("Replication cycle completed successfully.")
    except Exception as e:
        app_logger.error(f"Replication cron failed: {e}", exc_info=True)
