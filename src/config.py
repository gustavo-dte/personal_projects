"""
Configuration handling for the Service Bus replication function.
"""

from __future__ import annotations

from typing import List, Literal, Optional, cast

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    DEFAULT_BASE_RETRY_DELAY,
    DEFAULT_DELTA_MINUTES,
    DEFAULT_DLQ_ENABLED,
    DEFAULT_DLQ_TTL_MINUTES,
    DEFAULT_MAX_DELIVERY_COUNT,
    DEFAULT_MAX_RETRY_ATTEMPTS,
    DEFAULT_RTO_MINUTES,
    DIRECTION_PRIMARY_TO_SECONDARY,
    DIRECTION_SECONDARY_TO_PRIMARY,
    REPLICATION_TYPE_PRIMARY_TO_SECONDARY,
    REPLICATION_TYPE_SECONDARY_TO_PRIMARY,
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

    Note: Field names are kept as 'primary_queue' and 'secondary_queue' for
    backward compatibility, but they now represent topic names.
    """

    replication_type: Literal["primary_to_secondary", "secondary_to_primary"] = Field(
        default="primary_to_secondary",
        alias="REPLICATION_TYPE",
        description="Direction of message replication",
    )

    # Service Bus connection strings
    primary_conn_str: Optional[str] = Field(
        default=None,
        alias="PRIMARY_SERVICEBUS_CONN",
        description="Primary Service Bus connection string",
    )
    primary_queue: Optional[str] = Field(
        default=None,
        alias="PRIMARY_TOPIC_NAME",
        description="Primary Service Bus topic name",
    )
    secondary_conn_str: Optional[str] = Field(
        default=None,
        alias="SECONDARY_SERVICEBUS_CONN",
        description="Secondary Service Bus connection string",
    )
    secondary_queue: Optional[str] = Field(
        default=None,
        alias="SECONDARY_TOPIC_NAME",
        description="Secondary Service Bus topic name",
    )

    # Subscriptions
    primary_subscription_principal: Optional[str] = Field(
        default=None,
        alias="PRIMARY_SUBSCRIPTION_TOPIC_A",
        description="Principal subscription for the topic",
    )
    primary_subscription_additional: Optional[str] = Field(
        default=None,
        alias="PRIMARY_SUBSCRIPTION_TOPIC_B",
        description="Additional subscription for the topic",
    )
    subscription_list: List[str] = Field(
        default_factory=list,
        alias="SUBSCRIPTION_LIST",
        description="Comma-separated list of subscriptions to loop through",
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

    # -------- Validators --------
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

    @field_validator("subscription_list", mode="before")
    @classmethod
    def split_subscription_list(cls, v):
        if not v:
            return []
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    @model_validator(mode="after")
    def validate_connection_config(self):
        """Validate that required connection strings and queues are provided."""
        required_vars_map = {
            REPLICATION_TYPE_PRIMARY_TO_SECONDARY: [
                ("secondary_conn_str", "SECONDARY_SERVICEBUS_CONN"),
                ("secondary_queue", "SECONDARY_TOPIC_NAME"),
            ],
            REPLICATION_TYPE_SECONDARY_TO_PRIMARY: [
                ("primary_conn_str", "PRIMARY_SERVICEBUS_CONN"),
                ("primary_queue", "PRIMARY_TOPIC_NAME"),
            ],
        }

        required_fields = required_vars_map.get(self.replication_type, [])
        missing_fields = [
            env_var
            for field_name, env_var in required_fields
            if not getattr(self, field_name)
        ]

        if missing_fields:
            raise ConfigError(
                f"Missing required environment variables for "
                f"{self.replication_type}: {', '.join(missing_fields)}"
            )

        return self

    # -------- Convenience Properties --------
    @property
    def ttl_seconds(self) -> int:
        """Calculate the Time To Live for replicated messages in seconds."""
        total_minutes: int = self.rto_minutes + self.delta_minutes
        return total_minutes * SECONDS_PER_MINUTE

    @property
    def direction(self) -> str:
        """Return a readable description of the replication direction."""
        if self.replication_type == REPLICATION_TYPE_PRIMARY_TO_SECONDARY:
            return DIRECTION_PRIMARY_TO_SECONDARY
        return DIRECTION_SECONDARY_TO_PRIMARY

    def get_destination_config(self) -> tuple[str, str, str]:
        """
        Get destination connection information based on replication type.

        Returns:
            Tuple of (connection_string, topic_name, direction_description)
        """
        if self.replication_type == REPLICATION_TYPE_PRIMARY_TO_SECONDARY:
            return (
                cast(str, self.secondary_conn_str),
                cast(str, self.secondary_queue),
                self.direction,
            )

        return (
            cast(str, self.primary_conn_str),
            cast(str, self.primary_queue),
            self.direction,
        )

    @property
    def has_app_insights_config(self) -> bool:
        """Check if Application Insights configuration is available."""
        return bool(
            self.app_insights_connection_string or self.app_insights_instrumentation_key
        )


# Single instance for import
settings = ReplicationConfig()
