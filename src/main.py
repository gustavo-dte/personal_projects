"""
Improved Service Bus replication function following best practices.

This module implements Service Bus message replication with the following improvements:
- Separate functions for unit testing
- No nested functions
- Twelve Factor App methodology
- No hardcoded values
- Proper ConfigError and ValueError usage
- Pydantic for configuration validation
- Separation of concerns
"""

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
from azure.servicebus.exceptions import ServiceBusError
from pydantic import ValidationError as PydanticValidationError

from .config import ReplicationConfig
from .constants import (
    ALERT_SEVERITY_CRITICAL,
    ALERT_SEVERITY_HIGH,
)
from .exceptions import ConfigError, ReplicationError, ValidationError
from .logging_utils import (
    configure_logger,
    log_replication_error,
    log_replication_start,
    log_replication_success,
)
from .message_utils import create_replicated_message, generate_correlation_id
from .retry_utils import exponential_backoff_retry

# Configure the application logger
app_logger = configure_logger()


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
    destination_queue_name: str,
    message: ServiceBusMessage,
    correlation_id: str,
) -> None:
    """
    Send a message to the destination Service Bus queue.

    Args:
        destination_connection_string: Connection string for destination Service Bus
        destination_queue_name: Name of the destination queue
        message: The ServiceBusMessage to send
        correlation_id: Correlation ID for tracking

    Raises:
        Various Azure exceptions depending on what goes wrong during sending
    """
    with ServiceBusClient.from_connection_string(
        destination_connection_string
    ) as client:
        with client.get_queue_sender(queue_name=destination_queue_name) as queue_sender:
            queue_sender.send_messages(message)


def handle_authentication_error(
    error: ClientAuthenticationError,
    correlation_id: str,
    direction: str,
    destination_queue: str,
) -> None:
    """Handle authentication errors with appropriate logging and re-raising."""
    log_replication_error(
        logger=app_logger,
        correlation_id=correlation_id,
        error_type="authentication_error",
        error_message=str(error),
        direction=direction,
        destination_queue=destination_queue,
        alert_severity=ALERT_SEVERITY_CRITICAL,
    )
    raise ClientAuthenticationError(
        f"Failed to authenticate with Service Bus: {error}"
    ) from error


def handle_resource_not_found_error(
    error: ResourceNotFoundError,
    correlation_id: str,
    direction: str,
    destination_queue: str,
) -> None:
    """Handle resource not found errors with appropriate logging and re-raising."""
    log_replication_error(
        logger=app_logger,
        correlation_id=correlation_id,
        error_type="resource_not_found",
        error_message=str(error),
        direction=direction,
        destination_queue=destination_queue,
        alert_severity=ALERT_SEVERITY_HIGH,
    )
    raise ResourceNotFoundError(
        f"Could not find destination queue '{destination_queue}': {error}"
    ) from error


def handle_service_request_error(
    error: ServiceRequestError,
    correlation_id: str,
    direction: str,
    destination_queue: str,
) -> None:
    """Handle service request errors with appropriate logging and re-raising."""
    log_replication_error(
        logger=app_logger,
        correlation_id=correlation_id,
        error_type="service_request_error",
        error_message=str(error),
        direction=direction,
        destination_queue=destination_queue,
        alert_severity=ALERT_SEVERITY_HIGH,
    )
    raise ServiceRequestError(f"Service Bus request failed: {error}") from error


def handle_service_bus_error(
    error: ServiceBusError, correlation_id: str, direction: str, destination_queue: str
) -> None:
    """Handle Service Bus specific errors with appropriate logging and re-raising."""
    log_replication_error(
        logger=app_logger,
        correlation_id=correlation_id,
        error_type="servicebus_error",
        error_message=str(error),
        direction=direction,
        destination_queue=destination_queue,
        alert_severity=ALERT_SEVERITY_HIGH,
    )
    raise ServiceBusError(f"Service Bus operation failed: {error}") from error


def handle_http_response_error(
    error: HttpResponseError,
    correlation_id: str,
    direction: str,
    destination_queue: str,
) -> None:
    """Handle HTTP response errors with appropriate logging and re-raising."""
    additional_context = {"status_code": getattr(error, "status_code", None)}
    log_replication_error(
        logger=app_logger,
        correlation_id=correlation_id,
        error_type="http_response_error",
        error_message=str(error),
        direction=direction,
        destination_queue=destination_queue,
        alert_severity=ALERT_SEVERITY_HIGH,
        additional_context=additional_context,
    )
    raise HttpResponseError(
        f"HTTP request failed during message replication: {error}"
    ) from error


def handle_azure_error(
    error: AzureError, correlation_id: str, direction: str, destination_queue: str
) -> None:
    """Handle general Azure errors with appropriate logging and re-raising."""
    log_replication_error(
        logger=app_logger,
        correlation_id=correlation_id,
        error_type="azure_error",
        error_message=str(error),
        direction=direction,
        destination_queue=destination_queue,
        alert_severity=ALERT_SEVERITY_HIGH,
    )
    raise AzureError(
        f"Azure service error during message replication: {error}"
    ) from error


def handle_unexpected_error(
    error: Exception, correlation_id: str, direction: str, destination_queue: str
) -> None:
    """Handle unexpected errors with appropriate logging and re-raising."""
    log_replication_error(
        logger=app_logger,
        correlation_id=correlation_id,
        error_type="unexpected_error",
        error_message=str(error),
        direction=direction,
        destination_queue=destination_queue,
        alert_severity=ALERT_SEVERITY_CRITICAL,
    )
    raise RuntimeError(
        f"Unexpected error occurred during message replication: {error}"
    ) from error


def replicate_message_to_destination(
    source_message: func.ServiceBusMessage,
    destination_connection_string: str,
    destination_queue_name: str,
    ttl_seconds: int,
    direction: str,
    max_retry_attempts: int,
    base_retry_delay: float,
) -> None:
    """
    Replicate a Service Bus message to the destination queue with retry logic.

    This function handles the actual message replication logic with comprehensive
    error handling and retry capabilities.

    Args:
        source_message: The original Service Bus message to replicate
        destination_connection_string: Connection string for destination Service Bus
        destination_queue_name: Name of the destination queue
        ttl_seconds: Time-to-live for the replicated message in seconds
        direction: Human-friendly description of replication direction
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
        destination_queue=destination_queue_name,
        message_id=source_message.message_id,
        ttl_seconds=ttl_seconds,
    )

    # Create the retry decorator with configuration
    retry_decorator = exponential_backoff_retry(
        max_attempts=max_retry_attempts, base_delay=base_retry_delay, logger=app_logger
    )

    # Apply retry logic to the send operation
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
            destination_queue_name=destination_queue_name,
            message=replicated_message,
            correlation_id=correlation_id,
        )

        # Log successful replication
        source_body = source_message.get_body()
        log_replication_success(
            logger=app_logger,
            correlation_id=correlation_id,
            direction=direction,
            destination_queue=destination_queue_name,
            original_message_id=source_message.message_id,
            replicated_message_id=replicated_message.message_id,
            body_type=type(source_body).__name__,
            content_type=replicated_message.content_type or "unknown",
            body_size_bytes=len(replicated_message.get_body())
            if replicated_message.get_body()
            else 0,
        )

    try:
        # Execute the send operation with retry logic
        send_with_retry(correlation_id=correlation_id)

    except ClientAuthenticationError as auth_error:
        handle_authentication_error(
            auth_error, correlation_id, direction, destination_queue_name
        )
    except ResourceNotFoundError as resource_error:
        handle_resource_not_found_error(
            resource_error, correlation_id, direction, destination_queue_name
        )
    except ServiceRequestError as request_error:
        handle_service_request_error(
            request_error, correlation_id, direction, destination_queue_name
        )
    except ServiceBusError as sb_error:
        handle_service_bus_error(
            sb_error, correlation_id, direction, destination_queue_name
        )
    except HttpResponseError as http_error:
        handle_http_response_error(
            http_error, correlation_id, direction, destination_queue_name
        )
    except AzureError as azure_error:
        handle_azure_error(
            azure_error, correlation_id, direction, destination_queue_name
        )
    except Exception as unexpected_error:
        handle_unexpected_error(
            unexpected_error, correlation_id, direction, destination_queue_name
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
        dest_connection_string, dest_queue_name, direction = (
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
            destination_queue_name=dest_queue_name,
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

        # Orchestrate the replication process
        orchestrate_replication(source_message=msg, replication_config=config)

        app_logger.info("Service Bus replication function completed successfully")

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
