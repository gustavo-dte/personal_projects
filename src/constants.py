"""
Constants for the Service Bus replication function.

This module contains all constant values used throughout the application,
following the Twelve Factor App methodology by avoiding hardcoded values.
"""

# # Replication types
# REPLICATION_TYPE_PRIMARY_TO_SECONDARY: Literal["primary_to_secondary"] = (
#     "primary_to_secondary"
# )
# REPLICATION_TYPE_SECONDARY_TO_PRIMARY: Literal["secondary_to_primary"] = (
#     "secondary_to_primary"
# )

# # Direction labels
# DIRECTION_PRIMARY_TO_SECONDARY = "Primary → Secondary"
# DIRECTION_SECONDARY_TO_PRIMARY = "Secondary → Primary"

# Connection string environment variables with type annotations
ENV_PRIMARY_SERVICEBUS_CONN: str = "PRIMARY_SERVICEBUS_CONN"
ENV_SECONDARY_SERVICEBUS_CONN: str = "SECONDARY_SERVICEBUS_CONN"
# Environment variable names
# ENV_REPLICATION_TYPE = "REPLICATION_TYPE"
ENV_PRIMARY_SERVICEBUS_CONN = "PRIMARY_SERVICEBUS_CONN"
# ENV_PRIMARY_QUEUE_NAME = "PRIMARY_QUEUE_NAME"
ENV_SECONDARY_SERVICEBUS_CONN = "SECONDARY_SERVICEBUS_CONN"
# ENV_SECONDARY_QUEUE_NAME = "SECONDARY_QUEUE_NAME"
ENV_RTO_MINUTES = "RTO_MINUTES"
ENV_DELTA_MINUTES = "DELTA_MINUTES"
ENV_DLQ_ENABLED = "DLQ_ENABLED"
ENV_MAX_DELIVERY_COUNT = "MAX_DELIVERY_COUNT"
ENV_DLQ_TTL_MINUTES = "DLQ_TTL_MINUTES"
ENV_MAX_RETRY_ATTEMPTS = "MAX_RETRY_ATTEMPTS"
ENV_BASE_RETRY_DELAY = "BASE_RETRY_DELAY"

# Default values
DEFAULT_RTO_MINUTES = 10
DEFAULT_DELTA_MINUTES = 2
DEFAULT_DLQ_ENABLED = True
DEFAULT_MAX_DELIVERY_COUNT = 3
DEFAULT_DLQ_TTL_MINUTES = 1440  # 24 hours
DEFAULT_MAX_RETRY_ATTEMPTS = 3
DEFAULT_BASE_RETRY_DELAY = 1.0

# Content types
CONTENT_TYPE_BINARY = "application/octet-stream"
CONTENT_TYPE_TEXT_UTF8 = "text/plain; charset=utf-8"

# Logging configuration
LOGGER_NAME = "servicebus.replication"

# Alert severity levels
ALERT_SEVERITY_LOW = "low"
ALERT_SEVERITY_MEDIUM = "medium"
ALERT_SEVERITY_HIGH = "high"
ALERT_SEVERITY_CRITICAL = "critical"

# Message property keys
PROP_ORIGINAL_MESSAGE_ID = "x-original-message-id"
PROP_REPLICATION_CORRELATION_ID = "x-replication-correlation-id"
PROP_REPLICATION_TIMESTAMP = "x-replication-timestamp"

# Correlation ID prefix
CORRELATION_ID_PREFIX = "repl"

# Time conversion
SECONDS_PER_MINUTE = 60
