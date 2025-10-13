from typing import Optional, Literal, cast
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
    max_attempts: int = Field(default=DEFAULT_MAX_RETRY_ATTEMPTS, ge=1, le=10)
    base_delay: float = Field(default=DEFAULT_BASE_RETRY_DELAY, ge=0.1, le=60.0)


class DeadLetterConfig(BaseModel):
    enabled: bool = Field(default=DEFAULT_DLQ_ENABLED)
    max_delivery_count: int = Field(default=DEFAULT_MAX_DELIVERY_COUNT, ge=1, le=100)
    ttl_minutes: int = Field(default=DEFAULT_DLQ_TTL_MINUTES, ge=1, le=43200)


class ReplicationConfig(BaseSettings):
    """Configuration for Service Bus message replication."""

    replication_type: Literal["primary_to_secondary", "secondary_to_primary"] = Field(
        default="primary_to_secondary", alias="REPLICATION_TYPE"
    )

    # ✅ Connection strings only (topic names discovered dynamically)
    primary_conn_str: Optional[str] = Field(
        default=None, alias="PRIMARY_SERVICEBUS_CONN"
    )
    secondary_conn_str: Optional[str] = Field(
        default=None, alias="SECONDARY_SERVICEBUS_CONN"
    )

    # Optional legacy fields
    primary_queue: Optional[str] = Field(default=None, alias="PRIMARY_TOPIC_NAME")
    secondary_queue: Optional[str] = Field(default=None, alias="SECONDARY_TOPIC_NAME")

    # Timing
    rto_minutes: int = Field(default=DEFAULT_RTO_MINUTES, alias="RTO_MINUTES", ge=1)
    delta_minutes: int = Field(default=DEFAULT_DELTA_MINUTES, alias="DELTA_MINUTES", ge=0)

    retry_config: RetryConfig = Field(default_factory=RetryConfig)
    dead_letter_config: DeadLetterConfig = Field(default_factory=DeadLetterConfig)

    model_config = SettingsConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_connection_config(self):
        """Only connection strings are mandatory."""
        if not self.primary_conn_str or not self.secondary_conn_str:
            raise ConfigError(
                "Missing required environment variables: PRIMARY_SERVICEBUS_CONN and SECONDARY_SERVICEBUS_CONN"
            )
        return self

    @property
    def ttl_seconds(self) -> int:
        total_minutes: int = self.rto_minutes + self.delta_minutes
        return total_minutes * SECONDS_PER_MINUTE

    @property
    def direction(self) -> str:
        if self.replication_type == REPLICATION_TYPE_PRIMARY_TO_SECONDARY:
            return DIRECTION_PRIMARY_TO_SECONDARY
        return DIRECTION_SECONDARY_TO_PRIMARY
