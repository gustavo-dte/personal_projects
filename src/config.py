"""
Configuration handling for the Service Bus replication function.
"""

from __future__ import annotations

from typing import Optional, Union, cast  # noqa: F401

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    DEFAULT_BASE_RETRY_DELAY,
    DEFAULT_DELTA_MINUTES,
    DEFAULT_DLQ_ENABLED,
    DEFAULT_DLQ_TTL_MINUTES,
    DEFAULT_MAX_DELIVERY_COUNT,
    DEFAULT_MAX_RETRY_ATTEMPTS,
    DEFAULT_RTO_MINUTES,
    SECONDS_PER_MINUTE,
)
from .exceptions import ConfigError


class RetryConfig(BaseModel):
    """Configuration for retry behavior."""

    max_attempts: int = Field(
        default=DEFAULT_MAX_RETRY_ATTEMPTS,
        ge=1,
        le=10,
        description="Maximum number of retry attempts",
    )
    base_delay: float = Field(
        default=DEFAULT_BASE_RETRY_DELAY,
        ge=0.1,
        le=60.0,
        description="Base delay in seconds for exponential backoff",
    )


class DeadLetterConfig(BaseModel):
    """Configuration for dead letter queue handling."""

    enabled: bool = Field(
        default=DEFAULT_DLQ_ENABLED, description="Enable dead letter queue processing"
    )
    max_delivery_count: int = Field(
        default=DEFAULT_MAX_DELIVERY_COUNT,
        ge=1,
        le=100,
        description="Maximum delivery attempts before dead lettering",
    )
    ttl_minutes: int = Field(
        default=DEFAULT_DLQ_TTL_MINUTES,
        ge=1,
        le=43200,  # 30 days
        description="Time to live for messages in dead letter queue (minutes)",
    )


class ReplicationConfig(BaseSettings):
    """
    Configuration for Service Bus message replication.

    This Pydantic settings model automatically loads configuration from
    environment variables following the Twelve Factor App methodology.

    Required environment variables:
    - PRIMARY_SERVICEBUS_CONN: Source Service Bus connection string
    - SECONDARY_SERVICEBUS_CONN: Destination Service Bus connection string

    The function will dynamically discover all topics and subscriptions in the
    primary namespace and replicate messages to corresponding topics in the
    secondary namespace.
    """

    # Service Bus connection strings
    primary_conn_str: Optional[str] = Field(
        default=None,
        alias="PRIMARY_SERVICEBUS_CONN",
        description="Primary Service Bus connection string",
    )
    secondary_conn_str: Optional[str] = Field(
        default=None,
        alias="SECONDARY_SERVICEBUS_CONN",
        description="Secondary Service Bus connection string",
    )

    # Timing configuration
    rto_minutes: int = Field(
        default=DEFAULT_RTO_MINUTES,
        alias="RTO_MINUTES",
        ge=1,
        le=1440,  # 24 hours
        description="Recovery Time Objective in minutes",
    )
    delta_minutes: int = Field(
        default=DEFAULT_DELTA_MINUTES,
        alias="DELTA_MINUTES",
        ge=0,
        le=1440,
        description="Additional buffer time in minutes",
    )

    # Nested configuration objects
    retry_config: RetryConfig = Field(
        default_factory=RetryConfig, description="Retry configuration"
    )
    dead_letter_config: DeadLetterConfig = Field(
        default_factory=DeadLetterConfig, description="Dead letter queue configuration"
    )

    # Application Insights / Azure Monitor configuration
    app_insights_connection_string: Optional[str] = Field(
        default=None,
        alias="APPLICATIONINSIGHTS_CONNECTION_STRING",
        description="Application Insights connection string for telemetry",
    )
    app_insights_instrumentation_key: Optional[str] = Field(
        default=None,
        alias="APPINSIGHTS_INSTRUMENTATIONKEY",
        description="Application Insights instrumentation key for telemetry",
    )

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=True,
        env_nested_delimiter="_",
        extra="forbid",
    )

    @model_validator(mode="after")
    def validate_connection_config(self):
        """Validate that required connection strings are provided."""
        # For dynamic replication, both primary and secondary
        # connection strings are required
        if not self.primary_conn_str:
            raise ConfigError(
                "PRIMARY_SERVICEBUS_CONN is required for dynamic replication"
            )

        if not self.secondary_conn_str:
            raise ConfigError(
                "SECONDARY_SERVICEBUS_CONN is required for dynamic replication"
            )

        return self

    @property
    def ttl_seconds(self) -> int:
        """Calculate the Time To Live for replicated messages in seconds."""
        total_minutes: int = self.rto_minutes + self.delta_minutes
        return total_minutes * SECONDS_PER_MINUTE

    @property
    def direction(self) -> str:
        """Return a readable description of the replication direction."""
        return "Primary → Secondary"

    def get_destination_config(self, topic_name: str) -> tuple[str, str, str]:
        """
        Get destination connection information.

        Args:
            topic_name: The name of the topic to replicate to

        Returns:
            Tuple of (connection_string, topic_name, direction_description)

        Note:
            Validation is handled by Pydantic validators during model instantiation,
            so configuration is guaranteed to be valid when this method is called.

        Raises:
            ConfigError: If any required configuration is missing
        """
        # If we have both connection strings, use secondary as destination
        if self.primary_conn_str and self.secondary_conn_str:
            return (cast(str, self.secondary_conn_str), topic_name, self.direction)
        # If we only have primary connection, use it
        elif self.primary_conn_str:
            return (cast(str, self.primary_conn_str), topic_name, self.direction)
        # Otherwise use secondary connection
        return (cast(str, self.secondary_conn_str), topic_name, self.direction)

    @property
    def has_app_insights_config(self) -> bool:
        """Check if Application Insights configuration is available."""
        return bool(
            self.app_insights_connection_string or self.app_insights_instrumentation_key
        )
