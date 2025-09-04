import datetime
import logging

import azure.functions as func
from azure.core.exceptions import (
    AzureError,
    ClientAuthenticationError,
    HttpResponseError,
    ResourceNotFoundError,
    ServiceRequestError,
)
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus.exceptions import ServiceBusError

from .config import ReplicationConfig

# Configure OpenTelemetry to use Azure Monitor with the
# APPLICATIONINSIGHTS_CONNECTION_STRING environment variable.
# This provides automatic telemetry collection for monitoring and alerting
try:
    from azure.monitor.opentelemetry import configure_azure_monitor

    configure_azure_monitor(
        logger_name="servicebus.replication",  # Namespace for replication telemetry
    )
    # Create logger for this specific replication service
    app_logger = logging.getLogger("servicebus.replication")
    app_logger.info("Azure Monitor OpenTelemetry configured successfully")
except ImportError:
    # Azure Monitor OpenTelemetry not available - use standard logging
    app_logger = logging.getLogger(__name__)
    app_logger.info("Azure Monitor OpenTelemetry not available, using standard logging")
except Exception as monitor_error:
    # Fallback to standard logging if Application Insights isn't configured
    app_logger = logging.getLogger(__name__)
    app_logger.warning(f"Failed to configure Azure Monitor: {monitor_error}")
    app_logger.info("Using standard logging without Application Insights integration")


class ReplicationConfigurationError(Exception):
    """Custom exception raised when there's an issue with replication configuration."""


def with_exponential_backoff(max_attempts: int = 3, base_delay: float = 1.0):
    """
    Decorator that implements exponential backoff retry for transient failures.

    This provides a fallback retry mechanism when tenacity is not available,
    or can be used alongside tenacity for specific retry logic.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds, will be exponentially increased
                   (default: 1.0)
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (ServiceRequestError, HttpResponseError, ServiceBusError) as e:
                    last_exception = e
                    if attempt < max_attempts - 1:  # Not the last attempt
                        delay = base_delay * (2**attempt)  # Exponential backoff
                        app_logger.warning(
                            f"Transient error on attempt {attempt + 1}, "
                            f"retrying in {delay}s",
                            extra={
                                "attempt": attempt + 1,
                                "max_attempts": max_attempts,
                                "delay_seconds": delay,
                                "error_type": type(e).__name__,
                                "error_message": str(e),
                                "alert_severity": "medium",
                            },
                        )
                        import time

                        time.sleep(delay)
                    else:
                        # Last attempt failed, log and re-raise
                        app_logger.error(
                            f"All {max_attempts} retry attempts failed",
                            extra={
                                "max_attempts": max_attempts,
                                "final_error_type": type(e).__name__,
                                "final_error_message": str(e),
                                "alert_severity": "high",
                            },
                        )

            # Re-raise the last exception if all retries failed
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


@with_exponential_backoff(max_attempts=3, base_delay=1.0)
def replicate_message(
    *,
    source_message: func.ServiceBusMessage,
    destination_connection_string: str,
    destination_queue_name: str,
    ttl_seconds: int,
    direction: str,
) -> None:
    """
    Replicates a Service Bus message to the destination queue.

    This function handles the actual message replication logic. We use keyword-only
    arguments to make the function calls more explicit and reduce the chance of
    parameter mix-ups.

    Args:
        source_message: The original Service Bus message that needs to be replicated
        destination_connection_string: Connection string for the destination Service Bus
        destination_queue_name: Name of the queue where the message should be replicated
        ttl_seconds: How long the replicated message should live (in seconds)
        direction: A human-friendly description of the replication direction for logs

    Raises:
        Various Azure exceptions depending on what goes wrong during replication
    """
    # Create a correlation ID for tracking this replication operation
    correlation_id = (
        source_message.correlation_id
        or f"repl-{datetime.datetime.utcnow().isoformat()}"
    )

    app_logger.debug(
        "Starting message replication",
        extra={
            "correlation_id": correlation_id,
            "direction": direction,
            "destination_queue": destination_queue_name,
            "message_id": source_message.message_id,
            "ttl_seconds": ttl_seconds,
        },
    )

    try:
        # Create the Service Bus client using the destination connection string
        with ServiceBusClient.from_connection_string(
            destination_connection_string
        ) as client:
            # Get a sender for the specific queue
            queue_sender = client.get_queue_sender(queue_name=destination_queue_name)

            with queue_sender:
                # Set up the TTL for the new message
                message_ttl = datetime.timedelta(seconds=ttl_seconds)

                # Create a new message with the same body and properties
                # Preserve important tracking information for correlation
                # Note: We create a new message_id to avoid duplicate detection issues
                # but preserve the original ID in application properties for tracking

                # Start with application properties and add our tracking info
                preserved_app_properties = (
                    getattr(source_message, "application_properties", {}) or {}
                )
                enhanced_app_properties = preserved_app_properties.copy()
                enhanced_app_properties["x-original-message-id"] = (
                    source_message.message_id
                )
                enhanced_app_properties["x-replication-correlation-id"] = correlation_id
                enhanced_app_properties["x-replication-timestamp"] = str(
                    datetime.datetime.utcnow()
                )

                # Handle message body correctly - preserve bytes as bytes,
                # handle text properly
                source_body = source_message.get_body()
                original_content_type = getattr(source_message, "content_type", None)

                # Determine the appropriate body and content type for replication
                if isinstance(source_body, bytes):
                    # Body is already bytes - pass through as-is for maximum fidelity
                    replicated_body = source_body
                    # Use original content type or default to binary if none specified
                    final_content_type = (
                        original_content_type or "application/octet-stream"
                    )
                elif isinstance(source_body, str):
                    # Body is string - encode to UTF-8 bytes and set appropriate
                    # content type
                    replicated_body = source_body.encode("utf-8")
                    # Set explicit UTF-8 content type if not already specified
                    final_content_type = (
                        original_content_type or "text/plain; charset=utf-8"
                    )
                else:
                    # Handle other types by converting to string first, then bytes
                    string_body = str(source_body)
                    replicated_body = string_body.encode("utf-8")
                    final_content_type = (
                        original_content_type or "text/plain; charset=utf-8"
                    )

                replicated_message = ServiceBusMessage(
                    replicated_body,
                    time_to_live=message_ttl,
                    # Preserve all message properties for complete replication
                    application_properties=enhanced_app_properties,
                    content_type=final_content_type,
                    correlation_id=correlation_id,  # Use our replication correlation ID
                    subject=getattr(source_message, "subject", None),
                    session_id=getattr(source_message, "session_id", None),
                    to=getattr(source_message, "to", None),
                    reply_to=getattr(source_message, "reply_to", None),
                    reply_to_session_id=getattr(
                        source_message, "reply_to_session_id", None
                    ),
                    partition_key=getattr(source_message, "partition_key", None),
                    scheduled_enqueue_time_utc=getattr(
                        source_message, "scheduled_enqueue_time_utc", None
                    ),
                    # Generate new message_id to avoid duplicate detection conflicts
                    # Original ID is preserved in x-original-message-id property
                    message_id=(
                        f"repl-{correlation_id[:8]}-{source_message.message_id}"
                        if source_message.message_id
                        else f"repl-{correlation_id[:8]}"
                    ),
                )

                # Send the message to the destination queue
                queue_sender.send_messages(replicated_message)

                app_logger.info(
                    "Message replication successful",
                    extra={
                        "correlation_id": correlation_id,
                        "direction": direction,
                        "destination_queue": destination_queue_name,
                        "original_message_id": source_message.message_id,
                        "replicated_message_id": replicated_message.message_id,
                        "replication_status": "success",
                        "body_type": type(source_body).__name__,
                        "content_type": final_content_type,
                        "body_size_bytes": len(replicated_body)
                        if replicated_body
                        else 0,
                    },
                )

    except ClientAuthenticationError as auth_error:
        # Authentication failures are critical and should trigger immediate alerts
        app_logger.error(
            "Service Bus authentication failed",
            extra={
                "correlation_id": correlation_id,
                "error_type": "authentication_error",
                "error_message": str(auth_error),
                "direction": direction,
                "destination_queue": destination_queue_name,
                "alert_severity": "critical",
            },
        )
        raise ClientAuthenticationError(
            f"Failed to authenticate with Service Bus: {auth_error}"
        ) from auth_error

    except ResourceNotFoundError as resource_error:
        # Missing queues indicate configuration issues
        app_logger.error(
            "Service Bus resource not found",
            extra={
                "correlation_id": correlation_id,
                "error_type": "resource_not_found",
                "error_message": str(resource_error),
                "direction": direction,
                "destination_queue": destination_queue_name,
                "alert_severity": "high",
            },
        )
        raise ResourceNotFoundError(
            f"Could not find destination queue '{destination_queue_name}': "
            f"{resource_error}"
        ) from resource_error

    except ServiceRequestError as request_error:
        # Network and transient errors - handled by retry mechanism
        app_logger.error(
            "Service Bus request failed",
            extra={
                "correlation_id": correlation_id,
                "error_type": "service_request_error",
                "error_message": str(request_error),
                "direction": direction,
                "destination_queue": destination_queue_name,
                "alert_severity": "high",
            },
        )
        raise ServiceRequestError(
            f"Service Bus request failed: {request_error}"
        ) from request_error

    except ServiceBusError as sb_error:
        # Service Bus specific errors
        app_logger.error(
            "Service Bus operation failed",
            extra={
                "correlation_id": correlation_id,
                "error_type": "servicebus_error",
                "error_message": str(sb_error),
                "direction": direction,
                "destination_queue": destination_queue_name,
                "alert_severity": "high",
            },
        )
        raise ServiceBusError(f"Service Bus operation failed: {sb_error}") from sb_error

    except HttpResponseError as http_error:
        # HTTP-level errors from Azure services
        app_logger.error(
            "HTTP request failed during replication",
            extra={
                "correlation_id": correlation_id,
                "error_type": "http_response_error",
                "error_message": str(http_error),
                "direction": direction,
                "destination_queue": destination_queue_name,
                "status_code": getattr(http_error, "status_code", None),
                "alert_severity": "high",
            },
        )
        raise HttpResponseError(
            f"HTTP request failed during message replication: {http_error}"
        ) from http_error

    except AzureError as azure_error:
        # Catch-all for other Azure-specific errors
        app_logger.error(
            "Azure service error during replication",
            extra={
                "correlation_id": correlation_id,
                "error_type": "azure_error",
                "error_message": str(azure_error),
                "direction": direction,
                "destination_queue": destination_queue_name,
                "alert_severity": "high",
            },
        )
        raise AzureError(
            f"Azure service error during message replication: {azure_error}"
        ) from azure_error

    except Exception as unexpected_error:
        # This catches anything we didn't anticipate - always good to have a fallback
        app_logger.error(
            "Unexpected error during replication",
            extra={
                "correlation_id": correlation_id,
                "error_type": "unexpected_error",
                "error_message": str(unexpected_error),
                "direction": direction,
                "destination_queue": destination_queue_name,
                "alert_severity": "critical",
            },
        )
        raise RuntimeError(
            f"Unexpected error occurred during message replication: {unexpected_error}"
        ) from unexpected_error


def load_config() -> ReplicationConfig:
    """
    Load and validate replication configuration from environment variables.

    This function encapsulates all configuration loading and validation logic,
    making it easily testable and reusable.

    Returns:
        ReplicationConfig: Validated configuration object

    Raises:
        ReplicationConfigurationError: If configuration is invalid or missing
    """
    try:
        replication_config = ReplicationConfig.from_environment()
        replication_config.validate_destination_config()

        app_logger.info(
            "Replication configuration loaded successfully",
            extra={
                "replication_type": replication_config.replication_type,
                "configuration_status": "loaded",
            },
        )

        return replication_config

    except ValueError as config_error:
        app_logger.error(
            "Configuration validation failed",
            extra={
                "error_type": "configuration_error",
                "error_message": str(config_error),
                "alert_severity": "high",
            },
        )
        raise ReplicationConfigurationError(str(config_error)) from config_error


def replicate(
    *, source_message: func.ServiceBusMessage, replication_config: ReplicationConfig
) -> None:
    """
    Replicate a message using the provided configuration.

    This function orchestrates the message replication process by determining
    the destination and calling the replication logic.

    Args:
        source_message: The Service Bus message to replicate
        replication_config: Validated replication configuration

    Raises:
        Various Azure exceptions based on replication failures
    """
    # Determine destination based on configuration
    (dest_connection_string, dest_queue_name, _) = (
        replication_config.get_destination_config()
    )

    app_logger.info(
        "Starting message replication process",
        extra={
            "direction": replication_config.direction,
            "replication_status": "starting",
        },
    )

    # Perform the actual message replication
    replicate_message(
        source_message=source_message,
        destination_connection_string=dest_connection_string,
        destination_queue_name=dest_queue_name,
        ttl_seconds=replication_config.ttl_seconds,
        direction=replication_config.direction,
    )


def main(msg: func.ServiceBusMessage) -> None:
    """
    Main entry point for the Azure Function.

    This function coordinates the replication process by loading configuration
    and orchestrating message replication. Kept minimal for testability.

    Args:
        msg: The Service Bus message that triggered this function
    """
    app_logger.info("Service Bus replication function started")

    # Load and validate configuration
    config = load_config()

    # Replicate the message
    replicate(source_message=msg, replication_config=config)

    app_logger.info("Service Bus replication function completed successfully")
