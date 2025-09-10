"""
Test constants for the Service Bus replication function.

This module contains constants used specifically for testing purposes.
"""

# Test connection strings (for testing purposes only)
TEST_SERVICEBUS_CONNECTION_STRING = "Endpoint=sb://test.servicebus.windows.net/"

# Test topic/queue names
TEST_PRIMARY_TOPIC_NAME = "test-primary-topic"
TEST_SECONDARY_TOPIC_NAME = "test-secondary-topic"
TEST_SUBSCRIPTION_NAME = "test-subscription"

# Test configuration values
TEST_RTO_MINUTES = 5
TEST_DELTA_MINUTES = 1
TEST_MAX_RETRY_ATTEMPTS = 2
TEST_BASE_RETRY_DELAY = 0.5
