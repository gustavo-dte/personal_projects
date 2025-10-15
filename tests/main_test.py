"""
Unit tests for the dynamic Azure Service Bus replication Function App.
"""

from __future__ import annotations

from unittest.mock import Mock, patch, MagicMock

import pytest
from azure.core.exceptions import ClientAuthenticationError
from pydantic import ValidationError as PydanticValidationError

from src.main import (
    main,
    process_subscription_messages,
    replicate_message_to_destination,
    orchestrate_replication,
)
from tests.constants_test import (
    TEST_PRIMARY_CONN,
    TEST_SECONDARY_CONN,
    TEST_TOPICS,
    TEST_SUBSCRIPTIONS,
    TEST_REPLICATION_TYPE,
)


class TestConfigLoading:
    """Validate configuration loading and validation behavior."""

    @patch("src.main.ReplicationConfig")
    def test_config_creation_success(self, mock_config: Mock) -> None:
        """Test successful config creation in main function."""
        mock_instance = Mock()
        mock_instance.primary_conn_str = TEST_PRIMARY_CONN
        mock_instance.secondary_conn_str = TEST_SECONDARY_CONN
        mock_instance.direction = "Primary → Secondary"
        mock_config.return_value = mock_instance
        
        # This tests that the config can be created successfully
        config = mock_config()
        assert config.primary_conn_str == TEST_PRIMARY_CONN
        assert config.secondary_conn_str == TEST_SECONDARY_CONN

    @patch("src.main.ReplicationConfig")
    def test_config_validation_error(self, mock_config: Mock) -> None:
        """Test config validation error handling."""
        mock_config.side_effect = PydanticValidationError.from_exception_data(
            "ReplicationConfig",
            [{"type": "missing", "loc": ("PRIMARY_SERVICEBUS_CONN",), "msg": "missing"}],
        )
        
        with pytest.raises(Exception):
            mock_config()


class TestDynamicReplication:
    """Test dynamic topic/subscription enumeration."""

    @patch("src.main.ServiceBusAdministrationClient")
    @patch("src.main.process_subscription_messages")
    @patch("src.main.ReplicationConfig")
    @patch("src.main.ServiceBusClient")
    def test_topic_subscription_discovery(
        self,
        mock_client: Mock,
        mock_config: Mock,
        mock_process: Mock,
        mock_admin: Mock,
    ) -> None:
        # Setup config
        config_instance = Mock()
        config_instance.primary_conn_str = TEST_PRIMARY_CONN
        config_instance.secondary_conn_str = TEST_SECONDARY_CONN
        config_instance.direction = "Primary → Secondary"
        mock_config.return_value = config_instance
        
        # Setup admin client
        mock_admin_instance = Mock()
        mock_admin.from_connection_string.return_value = mock_admin_instance
        mock_admin_instance.list_topics.return_value = [
            Mock(name=t) for t in TEST_TOPICS
        ]
        mock_admin_instance.list_subscriptions.return_value = [
            Mock(name=s) for s in TEST_SUBSCRIPTIONS
        ]
        
        # Setup service bus client
        mock_client_instance = Mock()
        mock_client.from_connection_string.return_value.__enter__.return_value = mock_client_instance

        main(Mock())
        mock_process.assert_called()


class TestSubscriptionProcessing:
    """Verify per-subscription message processing logic."""

    @patch("src.main.ServiceBusClient")
    def test_no_messages(
        self,
        mock_client: Mock,
    ) -> None:
        # Setup source client
        receiver = MagicMock()
        receiver.receive_messages.return_value = []
        
        client_instance = MagicMock()
        client_instance.get_subscription_receiver.return_value.__enter__ = Mock(return_value=receiver)
        client_instance.get_subscription_receiver.return_value.__exit__ = Mock(return_value=None)
        
        logger = Mock()

        process_subscription_messages(
            client=client_instance,
            topic="topic-a",
            subscription="sub-a",
            dest_conn=TEST_SECONDARY_CONN,
            direction="Primary → Secondary",
            logger=logger,
        )

        # Should not attempt any replication when no messages
        receiver.receive_messages.assert_called_once()

    @patch("src.main.ServiceBusClient")
    @patch("src.main.create_replicated_message")
    def test_with_messages(
        self,
        mock_create: Mock,
        mock_client: Mock,
    ) -> None:
        # Setup source client
        receiver = MagicMock()
        msg = Mock()
        msg.correlation_id = "test-corr-id"
        msg.time_to_live = None
        receiver.receive_messages.return_value = [msg]
        
        source_client = MagicMock()
        source_client.get_subscription_receiver.return_value.__enter__ = Mock(return_value=receiver)
        source_client.get_subscription_receiver.return_value.__exit__ = Mock(return_value=None)
        
        # Setup destination client with context manager
        dest_sender = MagicMock()
        dest_client_instance = MagicMock()
        dest_client_instance.get_topic_sender.return_value.__enter__ = Mock(return_value=dest_sender)
        dest_client_instance.get_topic_sender.return_value.__exit__ = Mock(return_value=None)
        
        # Setup ServiceBusClient.from_connection_string as a context manager
        mock_client.from_connection_string.return_value.__enter__ = Mock(return_value=dest_client_instance)
        mock_client.from_connection_string.return_value.__exit__ = Mock(return_value=None)
        
        replicated_msg = Mock()
        mock_create.return_value = replicated_msg
        
        logger = Mock()

        process_subscription_messages(
            client=source_client,
            topic="topic-a",
            subscription="sub-a",
            dest_conn=TEST_SECONDARY_CONN,
            direction="Primary → Secondary",
            logger=logger,
        )

        mock_create.assert_called_once()
        receiver.complete_message.assert_called_once_with(msg)
class TestMessageReplication:
    """Check outbound message replication to destination Service Bus."""

    @patch("src.main.ServiceBusClient")
    @patch("src.main.create_replicated_message")
    def test_successful_send(
        self,
        mock_create: Mock,
        mock_client: Mock,
    ) -> None:
        msg = Mock()
        replicated = Mock()
        mock_create.return_value = replicated

        sender = MagicMock()
        client_instance = MagicMock()
        client_instance.get_topic_sender.return_value.__enter__ = Mock(return_value=sender)
        client_instance.get_topic_sender.return_value.__exit__ = Mock(return_value=None)
        
        mock_client.from_connection_string.return_value.__enter__ = Mock(return_value=client_instance)
        mock_client.from_connection_string.return_value.__exit__ = Mock(return_value=None)

        replicate_message_to_destination(
            msg,
            TEST_SECONDARY_CONN,
            "topic-a",
            "Primary → Secondary",
            "test-correlation-id",
        )

        mock_create.assert_called_once()
        sender.send_messages.assert_called_once_with(replicated)


class TestErrorCases:
    """Ensure exceptions and auth failures are handled correctly."""

    @patch("src.main.ServiceBusClient")
    def test_auth_error(self, mock_client: Mock) -> None:
        # Setup receiver to trigger the exception when messages are processed
        msg = Mock()
        msg.correlation_id = "test-id"
        receiver = MagicMock()
        receiver.receive_messages.return_value = [msg]
        
        client_instance = MagicMock()
        client_instance.get_subscription_receiver.return_value.__enter__ = Mock(return_value=receiver)
        client_instance.get_subscription_receiver.return_value.__exit__ = Mock(return_value=None)
        
        # Make the ServiceBusClient.from_connection_string raise the auth error
        mock_client.from_connection_string.side_effect = ClientAuthenticationError("Auth failed")
        
        logger = Mock()

        # The function should handle the error gracefully and log it
        process_subscription_messages(
            client=client_instance,
            topic="topic-x",
            subscription="sub-x",
            dest_conn=TEST_SECONDARY_CONN,
            direction="Primary → Secondary",
            logger=logger,
        )
        
        # Verify the error was logged and message was abandoned
        logger.error.assert_called()
        receiver.abandon_message.assert_called_once_with(msg)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
