"""
Test constants for the Service Bus replication function.
"""

# Connection strings (dummy values for local tests)
TEST_PRIMARY_CONN = "Endpoint=sb://primary-test.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=mockkey"
TEST_SECONDARY_CONN = "Endpoint=sb://secondary-test.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=mockkey"

# Topics and subscriptions
TEST_TOPICS = ["topic-a", "topic-b"]
TEST_SUBSCRIPTIONS = ["sub-a", "sub-b"]

# Replication configuration defaults
TEST_REPLICATION_TYPE = "primary_to_secondary"
TEST_RTO_MINUTES = 10
TEST_DELTA_MINUTES = 2
TEST_MAX_RETRY_ATTEMPTS = 3
TEST_BASE_RETRY_DELAY = 1.0
