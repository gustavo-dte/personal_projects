"""
Error handlers for Service Bus replication operations.

This module contains specialized error handling functions for different types
of Azure and Service Bus exceptions, providing consistent logging and error
transformation across the application.
"""

import logging

from azure.core.exceptions import (
    AzureError,
    ClientAuthenticationError,
    HttpResponseError,
    ResourceNotFoundError,
    ServiceRequestError,
)
from azure.servicebus.exceptions import ServiceBusError

from src.shared.constants import ALERT_SEVERITY_CRITICAL, ALERT_SEVERITY_HIGH
from src.shared.exceptions import ReplicationError
from src.shared.logging_utils import log_replication_error


def handle_authentication_error(
    error: ClientAuthenticationError,
    correlation_id: str,
    direction: str,
    destination_topic: str,
    logger: logging.Logger,
) -> None:
    """Handle authentication errors with appropriate logging and re-raising."""
    log_replication_error(
        logger=logger,
        correlation_id=correlation_id,
        error_type="authentication_error",
        error_message=str(error),
        direction=direction,
        destination_queue=destination_topic,
        alert_severity=ALERT_SEVERITY_CRITICAL,
    )
    raise ClientAuthenticationError(
        f"Failed to authenticate with Service Bus: {error}"
    ) from error


def handle_resource_not_found_error(
    error: ResourceNotFoundError,
    correlation_id: str,
    direction: str,
    destination_topic: str,
    logger: logging.Logger,
) -> None:
    """Handle resource not found errors with appropriate logging and re-raising."""
    log_replication_error(
        logger=logger,
        correlation_id=correlation_id,
        error_type="resource_not_found",
        error_message=str(error),
        direction=direction,
        destination_queue=destination_topic,
        alert_severity=ALERT_SEVERITY_HIGH,
    )
    raise ResourceNotFoundError(
        f"Could not find destination topic '{destination_topic}': {error}"
    ) from error


def handle_service_request_error(
    error: ServiceRequestError,
    correlation_id: str,
    direction: str,
    destination_topic: str,
    logger: logging.Logger,
) -> None:
    """Handle service request errors with appropriate logging and re-raising."""
    log_replication_error(
        logger=logger,
        correlation_id=correlation_id,
        error_type="service_request_error",
        error_message=str(error),
        direction=direction,
        destination_queue=destination_topic,
        alert_severity=ALERT_SEVERITY_HIGH,
    )
    raise ServiceRequestError(f"Service Bus request failed: {error}") from error


def handle_service_bus_error(
    error: ServiceBusError,
    correlation_id: str,
    direction: str,
    destination_topic: str,
    logger: logging.Logger,
) -> None:
    """Handle Service Bus specific errors with appropriate logging and re-raising."""
    additional_context = {"status_code": getattr(error, "status_code", None)}
    log_replication_error(
        logger=logger,
        correlation_id=correlation_id,
        error_type="service_bus_error",
        error_message=str(error),
        direction=direction,
        destination_queue=destination_topic,
        alert_severity=ALERT_SEVERITY_HIGH,
        additional_context=additional_context,
    )
    raise ServiceBusError(f"Service Bus operation failed: {error}") from error


def handle_http_response_error(
    error: HttpResponseError,
    correlation_id: str,
    direction: str,
    destination_topic: str,
    logger: logging.Logger,
) -> None:
    """Handle HTTP response errors with appropriate logging and re-raising."""
    log_replication_error(
        logger=logger,
        correlation_id=correlation_id,
        error_type="http_response_error",
        error_message=str(error),
        direction=direction,
        destination_queue=destination_topic,
        alert_severity=ALERT_SEVERITY_HIGH,
    )
    raise HttpResponseError(f"HTTP request failed: {error}") from error


def handle_azure_error(
    error: AzureError,
    correlation_id: str,
    direction: str,
    destination_topic: str,
    logger: logging.Logger,
) -> None:
    """Handle general Azure errors with appropriate logging and re-raising."""
    log_replication_error(
        logger=logger,
        correlation_id=correlation_id,
        error_type="azure_error",
        error_message=str(error),
        direction=direction,
        destination_queue=destination_topic,
        alert_severity=ALERT_SEVERITY_HIGH,
    )
    raise AzureError(f"Azure operation failed: {error}") from error


def handle_unexpected_error(
    error: Exception,
    correlation_id: str,
    direction: str,
    destination_topic: str,
    logger: logging.Logger,
) -> None:
    """Handle unexpected errors with appropriate logging and re-raising."""
    log_replication_error(
        logger=logger,
        correlation_id=correlation_id,
        error_type="unexpected_error",
        error_message=str(error),
        direction=direction,
        destination_queue=destination_topic,
        alert_severity=ALERT_SEVERITY_CRITICAL,
    )
    raise ReplicationError(
        f"Unexpected error during message replication: {error}"
    ) from error
