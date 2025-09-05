"""
Configuration handling for the Service Bus replication function.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings

from .constants import (
    DEFAULT_BASE_RETRY_DELAY,
    DEFAULT_DELTA_MINUTES,
    DEFAULT_DLQ_ENABLED,
    DEFAULT_DLQ_TTL_MINUTES,
    DEFAULT_MAX_DELIVERY_COUNT,
    DEFAULT_MAX_RETRY_ATTEMPTS,
    DEFAULT_RTO_MINUTES,
    REPLICATION_TYPE_PRIMARY_TO_SECONDARY,
    REPLICATION_TYPE_SECONDARY_TO_PRIMARY,
    SECONDS_PER_MINUTE,
)
from .exceptions import ConfigError, ValidationError


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
    """

    replication_type: Literal["primary_to_secondary", "secondary_to_primary"] = Field(
        description="Direction of message replication"
    )

    # Service Bus connection strings
    primary_conn_str: str | None = Field(
        default=None, description="Primary Service Bus connection string"
    )
    primary_queue: str | None = Field(
        default=None, description="Primary Service Bus queue name"
    )
    secondary_conn_str: str | None = Field(
        default=None, description="Secondary Service Bus connection string"
    )
    secondary_queue: str | None = Field(
        default=None, description="Secondary Service Bus queue name"
    )

    # Timing configuration
    rto_minutes: int = Field(
        default=DEFAULT_RTO_MINUTES,
        ge=1,
        le=1440,  # 24 hours
        description="Recovery Time Objective in minutes",
    )
    delta_minutes: int = Field(
        default=DEFAULT_DELTA_MINUTES,
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

    class Config:
        """Pydantic configuration."""

        env_prefix = ""
        case_sensitive = True
        env_nested_delimiter = "_"
        # Map environment variables to nested fields
        fields = {
            "replication_type": {"env": "REPLICATION_TYPE"},
            "primary_conn_str": {"env": "PRIMARY_SERVICEBUS_CONN"},
            "primary_queue": {"env": "PRIMARY_QUEUE_NAME"},
            "secondary_conn_str": {"env": "SECONDARY_SERVICEBUS_CONN"},
            "secondary_queue": {"env": "SECONDARY_QUEUE_NAME"},
            "rto_minutes": {"env": "RTO_MINUTES"},
            "delta_minutes": {"env": "DELTA_MINUTES"},
        }

    @field_validator("replication_type")
    @classmethod
    def validate_replication_type(cls, v: str) -> str:
        """Validate replication type is one of allowed values."""
        allowed_types = [
            REPLICATION_TYPE_PRIMARY_TO_SECONDARY,
            REPLICATION_TYPE_SECONDARY_TO_PRIMARY,
        ]
        if v not in allowed_types:
            raise ValueError(
                f"Invalid replication type '{v}'. "
                f"Must be one of: {', '.join(allowed_types)}"
            )
        return v

    @model_validator(mode="after")
    def validate_connection_config(self):
        """Validate that required connection strings and queues are provided."""
        missing_fields = []

        if self.replication_type == REPLICATION_TYPE_PRIMARY_TO_SECONDARY:
            if not self.secondary_conn_str:
                missing_fields.append("SECONDARY_SERVICEBUS_CONN")
            if not self.secondary_queue:
                missing_fields.append("SECONDARY_QUEUE_NAME")
        elif self.replication_type == REPLICATION_TYPE_SECONDARY_TO_PRIMARY:
            if not self.primary_conn_str:
                missing_fields.append("PRIMARY_SERVICEBUS_CONN")
            if not self.primary_queue:
                missing_fields.append("PRIMARY_QUEUE_NAME")

        if missing_fields:
            raise ConfigError(
                f"Missing required environment variables for "
                f"{self.replication_type}: {', '.join(missing_fields)}"
            )

        return self

    @property
    def ttl_seconds(self) -> int:
        """Calculate the Time To Live for replicated messages in seconds."""
        total_minutes: int = self.rto_minutes + self.delta_minutes
        seconds: int = total_minutes * SECONDS_PER_MINUTE
        return seconds  # type: ignore[no-any-return] # we know this is an int due to type hints

    @property
    def direction(self) -> str:
        """Return a human-friendly description of the replication direction."""
        if self.replication_type == REPLICATION_TYPE_PRIMARY_TO_SECONDARY:
            return "Primary → Secondary"
        else:
            return "Secondary → Primary"

    def get_destination_config(self) -> tuple[str, str, str]:
        """
        Get destination connection information based on replication type.

        Returns:
            Tuple of (connection_string, queue_name, direction_description)

        Raises:
            ValidationError: If destination configuration is invalid
        """
        if self.replication_type == REPLICATION_TYPE_PRIMARY_TO_SECONDARY:
            if not self.secondary_conn_str or not self.secondary_queue:
                raise ValidationError(
                    "Secondary connection configuration is required for "
                    "primary_to_secondary replication"
                )
            return (self.secondary_conn_str, self.secondary_queue, self.direction)
        else:
            if not self.primary_conn_str or not self.primary_queue:
                raise ValidationError(
                    "Primary connection configuration is required for "
                    "secondary_to_primary replication"
                )
            return (self.primary_conn_str, self.primary_queue, self.direction)
