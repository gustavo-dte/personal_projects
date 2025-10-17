from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    DEFAULT_BASE_RETRY_DELAY,
    DEFAULT_DELTA_MINUTES,
    DEFAULT_DLQ_ENABLED,
    DEFAULT_DLQ_TTL_MINUTES,
    DEFAULT_MAX_DELIVERY_COUNT,
    DEFAULT_MAX_RETRY_ATTEMPTS,
    DEFAULT_REPLICATION_TYPE,
    DEFAULT_RTO_MINUTES,
    REPLICATION_TYPE_PRIMARY_TO_SECONDARY,
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

    Automatically loads configuration from environment variables
    (Twelve-Factor App compliant).
    """

    # --- Replication configuration ---
    replication_type: Literal["primary_to_secondary", "secondary_to_primary"] = Field(
        default=DEFAULT_REPLICATION_TYPE,
        alias="REPLICATION_TYPE",
        description="Direction of message replication",
    )

    # --- Connection strings ---
    primary_conn_str: str = Field(
        default="",
        alias="PRIMARY_SERVICEBUS_CONN",
        description="Primary Service Bus connection string",
    )
    secondary_conn_str: str = Field(
        default="",
        alias="SECONDARY_SERVICEBUS_CONN",
        description="Secondary Service Bus connection string",
    )

    # --- Timing configuration ---
    rto_minutes: int = Field(
        default=DEFAULT_RTO_MINUTES,
        alias="RTO_MINUTES",
        ge=1,
        le=1440,
        description="Recovery Time Objective in minutes",
    )
    delta_minutes: int = Field(
        default=DEFAULT_DELTA_MINUTES,
        alias="DELTA_MINUTES",
        ge=0,
        le=1440,
        description="Additional buffer time in minutes",
    )

    # --- Nested configuration ---
    retry_config: RetryConfig = Field(default_factory=RetryConfig)
    dead_letter_config: DeadLetterConfig = Field(default_factory=DeadLetterConfig)

    # --- Monitoring ---
    app_insights_connection_string: Optional[str] = Field(
        default=None,
        alias="APPLICATIONINSIGHTS_CONNECTION_STRING",
    )
    app_insights_instrumentation_key: Optional[str] = Field(
        default=None,
        alias="APPINSIGHTS_INSTRUMENTATIONKEY",
    )

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=True,
        env_nested_delimiter="_",
        extra="forbid",
    )

    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def validate_connection_config(self) -> ReplicationConfig:
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

    # ------------------------------------------------------------------

    @property
    def ttl_seconds(self) -> int:
        """Calculate the Time To Live for replicated messages in seconds."""
        return (self.rto_minutes + self.delta_minutes) * SECONDS_PER_MINUTE

    @property
    def direction(self) -> str:
        """Return a readable description of the replication direction."""
        if self.replication_type == REPLICATION_TYPE_PRIMARY_TO_SECONDARY:
            return "Primary → Secondary"
        else:  # REPLICATION_TYPE_SECONDARY_TO_PRIMARY
            return "Secondary → Primary"

    def get_destination_config(self, topic_name: str) -> tuple[str, str, str]:
        """Return destination connection info based on replication direction."""
        if self.replication_type == REPLICATION_TYPE_PRIMARY_TO_SECONDARY:
            return (self.secondary_conn_str, topic_name, self.direction)
        else:  # REPLICATION_TYPE_SECONDARY_TO_PRIMARY
            return (self.primary_conn_str, topic_name, self.direction)

    @property
    def source_conn_str(self) -> str:
        """Return the source connection string based on replication direction."""
        if self.replication_type == REPLICATION_TYPE_PRIMARY_TO_SECONDARY:
            return self.primary_conn_str
        else:  # REPLICATION_TYPE_SECONDARY_TO_PRIMARY
            return self.secondary_conn_str

    @property
    def has_app_insights_config(self) -> bool:
        """True if Application Insights configuration is present."""
        return bool(
            self.app_insights_connection_string or self.app_insights_instrumentation_key
        )
