"""
Test constants for the Service Bus replication function.

This module contains constants used specifically for testing purposes.
"""

# Test connection strings (for testing purposes only)
TEST_SERVICEBUS_CONNECTION_STRING = "Endpoint=sb://test.servicebus.windows.net/"
TEST_SECONDARY_CONNECTION_STRING = "Endpoint=sb://secondary.servicebus.windows.net/"

# Topics and subscriptions
TEST_TOPICS = ["topic-a", "topic-b"]
TEST_SUBSCRIPTIONS = ["sub-a", "sub-b"]

# Replication configuration defaults
TEST_REPLICATION_TYPE = "primary_to_secondary"
TEST_RTO_MINUTES = 10
TEST_DELTA_MINUTES = 2
TEST_MAX_RETRY_ATTEMPTS = 3
