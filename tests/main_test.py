"""
Unit tests for the dynamic Service Bus replication function.
"""

import pytest
from unittest.mock import patch, Mock
from azure.core.exceptions import ClientAuthenticationError
from pydantic import ValidationError as PydanticValidationError

from src.config import ReplicationConfig
from src.main import (
    main,
    load_config,
    process_subscription_messages,
    replicate_to_destination,
)
from src.message_utils import create_replicated_message
from tests.constants_test import (
    TEST_PRIMARY_CONN,
    TEST_SECONDARY_CONN,
    TEST_TOPICS,
    TEST_SUBSCRIPTIONS,
    TEST_REPLICATION_TYPE,
)


class TestConfigLoading:
    """Validate configuration initialization and environment reading."""

    @patch("src.main.ReplicationConfig")
    def test_load_config_success(self, mock_config):
        mock_instance = Mock()
        mock_config.return_value = mock_instance
        result = load_config()
        assert result == mock_instance
        mock_config.assert_called_once()

    @patch("src.main.ReplicationConfig")
    def test_load_config_validation_error(self, mock_config):
        mock_config.side_effect = PydanticValidationError.from_exception_data(
            "Config", [{"type": "missing", "loc": ("PRIMARY_SERVICEBUS_CONN",), "msg": "missing"}]
        )
        with pytest.raises(Exception):
            load_config()


class TestDynamicReplication:
    """Tests for the dynamic replication behavior."""

    @patch("src.main.ServiceBusAdministrationClient")
    def test_topic_subscription_discovery(self, mock_admin):
        """Validate that dynamic discovery retrieves topics and subscriptions."""
        mock_admin_instance = Mock()
        mock_admin.return_value = mock_admin_instance

        mock_admin_instance.list_topics.return_value = [Mock(name="topic", name_value=t) for t in TEST_TOPICS]
        mock_admin_instance.list_subscriptions.return_value = [
            Mock(subscription_name=s) for s in TEST_SUBSCRIPTIONS
        ]

        config = Mock()
        config.primary_conn_str = TEST_PRIMARY_CONN
        config.secondary_conn_str = TEST_SECONDARY_CONN
        config.replication_type = TEST_REPLICATION_TYPE

        with patch("src.main.process_subscription_messages") as mock_process:
            main(Mock())

        mock_process.assert_called()


class TestSubscriptionProcessing:
    """Unit test for process_subscription_messages."""

    @patch("src.main.replicate_to_destination")
    @patch("src.main.ServiceBusClient")
    def test_process_subscription_messages_no_messages(self, mock_client, mock_replicate):
        """Validate that it exits gracefully when no messages exist."""
        mock_receiver = Mock()
        mock_receiver.receive_messages.return_value = []
        mock_client.return_value.__enter__.return_value = mock_client
        mock_client.get_subscription_receiver.return_value = mock_receiver

        config = Mock()
        config.ttl_seconds = 300
        logger = Mock()

        process_subscription_messages(
            topic="topic-a",
            subscription="sub-a",
            source_conn=TEST_PRIMARY_CONN,
            dest_conn=TEST_SECONDARY_CONN,
            config=config,
            direction="Primary → Secondary",
            logger=logger,
        )

        mock_replicate.assert_not_called()

    @patch("src.main.replicate_to_destination")
    @patch("src.main.ServiceBusClient")
    def test_process_subscription_messages_with_messages(self, mock_client, mock_replicate):
        """Validate replication loop for active messages."""
        mock_receiver = Mock()
        mock_message = Mock()
        mock_receiver.receive_messages.return_value = [mock_message]
        mock_client.return_value.__enter__.return_value = mock_client
        mock_client.get_subscription_receiver.return_value = mock_receiver

        config = Mock()
        config.ttl_seconds = 600
        logger = Mock()

        process_subscription_messages(
            topic="topic-a",
            subscription="sub-a",
            source_conn=TEST_PRIMARY_CONN,
            dest_conn=TEST_SECONDARY_CONN,
            config=config,
            direction="Primary → Secondary",
            logger=logger,
        )

        mock_replicate.assert_called_once()


class TestMessageReplication:
    """Unit test for replicate_to_destination."""

    @patch("src.main.ServiceBusClient")
    @patch("src.main.create_replicated_message")
    def test_replicate_to_destination_success(self, mock_create, mock_client):
        """Ensure that replicate_to_destination sends a built message."""
        mock_message = Mock()
        mock_replicated = Mock()
        mock_create.return_value = mock_replicated

        mock_sender = Mock()
        mock_client_instance = Mock()
        mock_client_instance.get_topic_sender.return_value = mock_sender
        mock_client.return_value.__enter__.return_value = mock_client_instance

        replicate_to_destination(
            mock_message,
            TEST_SECONDARY_CONN,
            "topic-a",
            "sub-a",
            "Primary → Secondary",
            Mock(),
            Mock(),
        )

        mock_create.assert_called_once()
        mock_sender.send_messages.assert_called_once_with(mock_replicated)


class TestErrorCases:
    """Validate authentication and exception handling."""

    @patch("src.main.ServiceBusClient")
    def test_authentication_error_raises(self, mock_client):
        mock_client.side_effect = ClientAuthenticationError("Auth failed")
        config = Mock()
        logger = Mock()

        with pytest.raises(ClientAuthenticationError):
            process_subscription_messages(
                topic="topic-x",
                subscription="sub-x",
                source_conn=TEST_PRIMARY_CONN,
                dest_conn=TEST_SECONDARY_CONN,
                config=config,
                direction="Primary → Secondary",
                logger=logger,
            )


if __name__ == "__main__":
    pytest.main([__file__])
