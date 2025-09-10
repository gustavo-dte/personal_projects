"""
Logging utility functions for the Service Bus replication function.

This module provides centralized logging configuration and utility functions
following the Twelve Factor App methodology.
"""

import logging
from typing import Any

from azure.monitor.opentelemetry import configure_azure_monitor

from .config import ReplicationConfig
from .constants import ALERT_SEVERITY_HIGH, LOGGER_NAME


def configure_logger(config: ReplicationConfig | None = None) -> logging.Logger:
    """
    Configure and return the application logger.

    Sets up Azure Monitor OpenTelemetry integration if the appropriate
    connection string or instrumentation key is available in the configuration.
    Falls back to standard logging for development and testing environments.

    Args:
        config: Optional ReplicationConfig instance with Application Insights settings.
                If not provided, will create a new config instance to load from
                environment.

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(LOGGER_NAME)

    # Load configuration if not provided
    if config is None:
        try:
            config = ReplicationConfig()
        except Exception:
            # If config loading fails, use standard logging
            config = None

    # Check if Azure Monitor configuration is available
    has_app_insights_connection = (
        config and config.has_app_insights_config
    ) if config else False

    if has_app_insights_connection:
        try:
            configure_azure_monitor(
                logger_name=LOGGER_NAME,
            )
            logger.info("Azure Monitor OpenTelemetry configured successfully")
        except (ValueError, OSError) as monitor_error:
            logger.warning("Failed to configure Azure Monitor: %s", monitor_error)
            logger.info(
                "Using standard logging without Application Insights integration"
            )
    else:
        logger.info(
            "No Application Insights configuration found, using standard logging"
        )
        # Configure basic logging for development/testing
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    return logger


def log_replication_start(
    logger: logging.Logger,
    correlation_id: str,
    direction: str,
    destination_queue: str,
    message_id: str | None,
    ttl_seconds: int,
) -> None:
    """Log the start of message replication.

    Note: Parameter name kept as 'destination_queue' for backward compatibility with
    existing log analysis tools, but represents destination topic name.
    """
    logger.debug(
        "Starting message replication",
        extra={
            "correlation_id": correlation_id,
            "direction": direction,
            "destination_queue": destination_queue,
            "message_id": message_id,
            "ttl_seconds": ttl_seconds,
        },
    )


def log_replication_success(
    logger: logging.Logger,
    correlation_id: str,
    direction: str,
    destination_queue: str,
    original_message_id: str | None,
    replicated_message_id: str,
    body_type: str,
    content_type: str,
    body_size_bytes: int,
) -> None:
    """Log successful message replication.

    Note: Parameter name kept as 'destination_queue' for backward compatibility with
    existing log analysis tools, but represents destination topic name.
    """
    logger.debug(
        "Message replication successful",
        extra={
            "correlation_id": correlation_id,
            "direction": direction,
            "destination_queue": destination_queue,
            "original_message_id": original_message_id,
            "replicated_message_id": replicated_message_id,
            "replication_status": "success",
            "body_type": body_type,
            "content_type": content_type,
            "body_size_bytes": body_size_bytes,
        },
    )


def log_replication_error(
    logger: logging.Logger,
    correlation_id: str,
    error_type: str,
    error_message: str,
    direction: str,
    destination_queue: str,
    alert_severity: str = ALERT_SEVERITY_HIGH,
    additional_context: dict[str, Any] | None = None,
) -> None:
    """Log replication error with structured context.

    Note: Parameter name kept as 'destination_queue' for backward compatibility with
    existing log analysis tools, but represents destination topic name.
    """
    log_context = {
        "correlation_id": correlation_id,
        "error_type": error_type,
        "error_message": error_message,
        "direction": direction,
        "destination_queue": destination_queue,
        "alert_severity": alert_severity,
    }

    if additional_context:
        log_context.update(additional_context)

    logger.error(
        f"Service Bus replication error: {error_type}",
        extra=log_context,
    )
