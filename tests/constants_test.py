"""
Test constants used across Service Bus replication unit tests.
"""

TEST_PRIMARY_CONN: str = (
    "Endpoint=sb://primary-test.servicebus.windows.net/;"
    "SharedAccessKeyName=RootManageSharedAccessKey;"
    "SharedAccessKey=mockkey"
)
TEST_SECONDARY_CONN: str = (
    "Endpoint=sb://secondary-test.servicebus.windows.net/;"
    "SharedAccessKeyName=RootManageSharedAccessKey;"
    "SharedAccessKey=mockkey"
)

TEST_TOPICS: list[str] = ["topic-a", "topic-b"]
TEST_SUBSCRIPTIONS: list[str] = ["sub-a", "sub-b"]

TEST_REPLICATION_TYPE: str = "primary_to_secondary"
TEST_RTO_MINUTES: int = 10
TEST_DELTA_MINUTES: int = 2
TEST_MAX_RETRY_ATTEMPTS: int = 3
TEST_BASE_RETRY_DELAY: float = 1.0
