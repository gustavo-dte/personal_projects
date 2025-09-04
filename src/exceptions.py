"""
Custom exceptions for the Service Bus replication function.

This module defines custom exception classes following proper exception hierarchy
and naming conventions for different types of errors in the replication system.
"""


class ServiceBusReplicationError(Exception):
    """Base exception for all Service Bus replication related errors."""

    def __init__(self, message: str, correlation_id: str | None = None) -> None:
        super().__init__(message)
        self.correlation_id = correlation_id


class ConfigError(ServiceBusReplicationError):
    """Exception raised when there's an issue with configuration."""

    def __init__(self, message: str, field_name: str | None = None) -> None:
        super().__init__(message)
        self.field_name = field_name


class ReplicationError(ServiceBusReplicationError):
    """Exception raised when message replication fails."""

    def __init__(
        self, message: str, correlation_id: str | None = None, retry_count: int = 0
    ) -> None:
        super().__init__(message, correlation_id)
        self.retry_count = retry_count


class ValidationError(ServiceBusReplicationError):
    """Exception raised when validation fails."""

    def __init__(self, message: str, field_name: str | None = None) -> None:
        super().__init__(message)
        self.field_name = field_name
