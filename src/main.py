"""
Improved Service Bus replication function following best practices.
This module implements Service Bus message replication
"""

import logging
from typing import Any

import azure.functions as func
from azure.core.exceptions import (AzureError, ClientAuthenticationError,
                                   HttpResponseError, ResourceNotFoundError,
                                   ServiceRequestError)
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus.exceptions import ServiceBusError
from pydantic import ValidationError as PydanticValidationError

from .config import ReplicationConfig
from .constants import ALERT_SEVERITY_CRITICAL, ALERT_SEVERITY_HIGH
from .error_handlers import (handle_authentication_error, handle_azure_error,
                             handle_http_response_error,
                             handle_resource_not_found_error,
                             handle_service_bus_error,
                             handle_service_request_error,
                             handle_unexpected_error)
from .exceptions import ConfigError, ReplicationError, ValidationError
from .logging_utils import (configure_logger, log_replication_start,
                            log_replication_success)
from .message_utils import create_replicated_message, generate_correlation_id
from .retry_utils import exponential_backoff_retry

# Configure the initial logger (will be reconfigured with config later)
app_logger = configure_logger()


def configure_application_logging(config: ReplicationConfig) -> logging.Logger:
    """
    Configure application logging with proper configuration.

    Args:
        config: ReplicationConfig instance with Application Insights settings

    Returns:
        Configured logger instance
    """
    return configure_logger(config)


def load_and_validate_config() -> ReplicationConfig:
    """
    Load and validate replication configuration from environment variables.

    This function encapsulates all configuration loading and validation logic,
    making it easily testable and reusable.

    Returns:
        ReplicationConfig: Validated configuration object

    Raises:
        ConfigError: If configuration is invalid or missing
    """
    try:
        config = ReplicationConfig()
        app_logger.info(
            "Replication configuration loaded successfully",
            extra={
                "replication_type": config.replication_type,
                "configuration_status": "loaded",
            },
        )
        return config

    except PydanticValidationError as validation_error:
        error_message = f"Configuration validation failed: {validation_error}"
        app_logger.error(
            "Configuration validation failed",
            extra={
                "error_type": "configuration_error",
                "error_message": error_message,
                "alert_severity": ALERT_SEVERITY_HIGH,
            },
        )
        raise ConfigError(error_message) from validation_error

    except Exception as unexpected_error:
        error_message = f"Unexpected error loading configuration: {unexpected_error}"
        app_logger.error(
            "Unexpected configuration error",
            extra={
                "error_type": "unexpected_configuration_error",
                "error_message": error_message,
                "alert_severity": ALERT_SEVERITY_CRITICAL,
            },
        )
        raise ConfigError(error_message) from unexpected_error


def send_message_to_destination(
    destination_connection_string: str,
    destination_topic_name: str,
    message: ServiceBusMessage,
    correlation_id: str,
) -> None:
    """
    Send a message to the destination Service Bus topic.

    Args:
        destination_connection_string: Connection string for destination Service Bus
        destination_topic_name: Name of the destination topic
        message: The ServiceBusMessage to send
        correlation_id: Correlation ID for tracking

    Raises:
        Various Azure exceptions depending on what goes wrong during sending
    """
    app_logger.debug(
        "Sending message to destination topic",
        extra={
            "correlation_id": correlation_id,
            "destination_topic": destination_topic_name,
            "message_id": getattr(message, "message_id", None),
        },
    )

    with ServiceBusClient.from_connection_string(
        destination_connection_string
    ) as client:
        with client.get_topic_sender(topic_name=destination_topic_name) as topic_sender:
            topic_sender.send_messages(message)


def _create_retry_send_function(
    source_message: func.ServiceBusMessage,
    destination_connection_string: str,
    destination_topic_name: str,
    ttl_seconds: int,
    direction: str,
    correlation_id: str,
    retry_decorator: Any,
) -> Any:
    """
    Create a retry-enabled send function with proper logging.

    This extracted function reduces complexity by separating the retry logic
    and success logging from the main replication flow.

    Args:
        source_message: The original Service Bus message
        destination_connection_string: Destination connection string
        destination_topic_name: Name of destination topic
        ttl_seconds: Time-to-live for message
        direction: Replication direction description
        correlation_id: Tracking correlation ID
        retry_decorator: Configured retry decorator

    Returns:
        Decorated function ready for execution
    """

    @retry_decorator
    def send_with_retry(**kwargs: Any) -> None:
        # Create the replicated message
        replicated_message = create_replicated_message(
            source_message=source_message,
            correlation_id=correlation_id,
            ttl_seconds=ttl_seconds,
        )

        # Send to destination
        send_message_to_destination(
            destination_connection_string=destination_connection_string,
            destination_topic_name=destination_topic_name,
            message=replicated_message,
            correlation_id=correlation_id,
        )

        # Log successful replication
        _log_successful_replication(
            source_message,
            replicated_message,
            correlation_id,
            direction,
            destination_topic_name,
        )

    return send_with_retry


def _log_successful_replication(
    source_message: func.ServiceBusMessage,
    replicated_message: func.ServiceBusMessage,
    correlation_id: str,
    direction: str,
    destination_topic_name: str,
) -> None:
    """
    Log successful message replication with detailed metrics.

    This extracted function reduces complexity by isolating logging logic
    and makes the success logging reusable.

    Args:
        source_message: Original message
        replicated_message: New replicated message
        correlation_id: Tracking correlation ID
        direction: Replication direction description
        destination_topic_name: Name of destination topic
    """
    source_body = source_message.get_body()
    log_replication_success(
        logger=app_logger,
        correlation_id=correlation_id,
        direction=direction,
        destination_queue=destination_topic_name,
        original_message_id=source_message.message_id,
        replicated_message_id=replicated_message.message_id,
        body_type=type(source_body).__name__,
        content_type=replicated_message.content_type or "unknown",
        body_size_bytes=len(replicated_message.get_body())
        if replicated_message.get_body()
        else 0,
    )


def _handle_replication_exceptions(
    send_function: Any,
    correlation_id: str,
    direction: str,
    destination_topic_name: str,
    logger: logging.Logger,
) -> None:
    """
    Execute send function with comprehensive exception handling.

    This extracted function reduces the main function's cyclomatic complexity
    by centralizing all exception handling logic.

    Args:
        send_function: The retry-enabled send function to execute
        correlation_id: Tracking correlation ID
        direction: Replication direction description
        destination_topic_name: Name of destination topic
        logger: Logger instance for error handling

    Raises:
        Various Azure exceptions after proper error handling
    """
    try:
        send_function(correlation_id=correlation_id)
    except ClientAuthenticationError as auth_error:
        handle_authentication_error(
            auth_error, correlation_id, direction, destination_topic_name, logger
        )
    except ResourceNotFoundError as resource_error:
        handle_resource_not_found_error(
            resource_error, correlation_id, direction, destination_topic_name, logger
        )
    except ServiceRequestError as request_error:
        handle_service_request_error(
            request_error, correlation_id, direction, destination_topic_name, logger
        )
    except ServiceBusError as sb_error:
        handle_service_bus_error(
            sb_error, correlation_id, direction, destination_topic_name, logger
        )
    except HttpResponseError as http_error:
        handle_http_response_error(
            http_error, correlation_id, direction, destination_topic_name, logger
        )
    except AzureError as azure_error:
        handle_azure_error(
            azure_error, correlation_id, direction, destination_topic_name, logger
        )
    except Exception as unexpected_error:
        handle_unexpected_error(
            unexpected_error, correlation_id, direction, destination_topic_name, logger
        )


def replicate_message_to_destination(
    source_message: func.ServiceBusMessage,
    destination_connection_string: str,
    destination_topic_name: str,
    ttl_seconds: int,
    direction: str,
    max_retry_attempts: int,
    base_retry_delay: float,
) -> None:
    """
    Replicate a Service Bus message to the destination topic with retry logic.

    This function orchestrates the message replication process by coordinating
    correlation ID generation, logging, retry configuration, and error handling.
    Complexity has been reduced through function extraction following SRP.

    Args:
        source_message: The original Service Bus message to replicate
        destination_connection_string: Connection string for destination Service Bus
        destination_queue_name: Name of the destination queue
        ttl_seconds: Time-to-live for the replicated message in seconds
        direction: Readable description of replication direction
        max_retry_attempts: Maximum number of retry attempts
        base_retry_delay: Base delay for exponential backoff

    Raises:
        Various Azure exceptions depending on what goes wrong during replication
    """
    # Generate correlation ID for tracking
    correlation_id = generate_correlation_id(source_message)

    # Log the start of replication
    log_replication_start(
        logger=app_logger,
        correlation_id=correlation_id,
        direction=direction,
        destination_queue=destination_topic_name,
        message_id=source_message.message_id,
        ttl_seconds=ttl_seconds,
    )

    # Create the retry decorator with configuration
    retry_decorator = exponential_backoff_retry(
        max_attempts=max_retry_attempts, base_delay=base_retry_delay, logger=app_logger
    )

    # Create retry-enabled send function
    send_with_retry = _create_retry_send_function(
        source_message=source_message,
        destination_connection_string=destination_connection_string,
        destination_topic_name=destination_topic_name,
        ttl_seconds=ttl_seconds,
        direction=direction,
        correlation_id=correlation_id,
        retry_decorator=retry_decorator,
    )

    # Execute with comprehensive error handling
    _handle_replication_exceptions(
        send_function=send_with_retry,
        correlation_id=correlation_id,
        direction=direction,
        destination_topic_name=destination_topic_name,
        logger=app_logger,
    )


def orchestrate_replication(
    source_message: func.ServiceBusMessage, replication_config: ReplicationConfig
) -> None:
    """
    Orchestrate the message replication process using the provided configuration.

    This function coordinates the message replication by extracting destination
    configuration and delegating to the replication function.

    Args:
        source_message: The Service Bus message to replicate
        replication_config: Validated replication configuration

    Raises:
        ValidationError: If destination configuration is invalid
        Various Azure exceptions based on replication failures
    """
    try:
        # Extract destination configuration
        dest_connection_string, dest_topic_name, direction = (
            replication_config.get_destination_config()
        )

        app_logger.debug(
            "Starting message replication process",
            extra={
                "direction": direction,
                "replication_status": "starting",
            },
        )

        # Perform the actual message replication
        replicate_message_to_destination(
            source_message=source_message,
            destination_connection_string=dest_connection_string,
            destination_topic_name=dest_topic_name,
            ttl_seconds=replication_config.ttl_seconds,
            direction=direction,
            max_retry_attempts=replication_config.retry_config.max_attempts,
            base_retry_delay=replication_config.retry_config.base_delay,
        )

    except ValidationError as validation_error:
        app_logger.error(
            "Destination configuration validation failed",
            extra={
                "error_type": "validation_error",
                "error_message": str(validation_error),
                "alert_severity": ALERT_SEVERITY_HIGH,
            },
        )
        raise


def main(msg: func.ServiceBusMessage) -> None:
    """
    Main entry point for the Azure Function.

    This function coordinates the replication process by loading configuration
    and orchestrating message replication. Designed for testability and
    clear separation of concerns.

    Args:
        msg: The Service Bus message that triggered this function
    """
    app_logger.info("Service Bus replication function started")

    try:
        # Load and validate configuration
        config = load_and_validate_config()

        # Reconfigure logger with proper Application Insights settings
        logger = configure_application_logging(config)
        logger.info("Logger reconfigured with Application Insights settings")

        # Orchestrate the replication process
        orchestrate_replication(source_message=msg, replication_config=config)

        logger.info("Service Bus replication function completed successfully")

    except (ConfigError, ValidationError, ReplicationError) as known_error:
        app_logger.error(
            "Service Bus replication failed with known error",
            extra={
                "error_type": type(known_error).__name__,
                "error_message": str(known_error),
                "alert_severity": ALERT_SEVERITY_HIGH,
            },
        )
        raise

    except Exception as unexpected_error:
        app_logger.error(
            "Service Bus replication failed with unexpected error",
            extra={
                "error_type": "unexpected_main_error",
                "error_message": str(unexpected_error),
                "alert_severity": ALERT_SEVERITY_CRITICAL,
            },
        )
        raise RuntimeError(
            f"Unexpected error in Service Bus replication: {unexpected_error}"
        ) from unexpected_error
