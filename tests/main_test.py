"""
Unit tests for the dynamic Azure Service Bus replication Function App.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from azure.core.exceptions import ClientAuthenticationError
from pydantic import ValidationError as PydanticValidationError

from src.main import (
    load_config,
    main,
    process_subscription_messages,
    replicate_to_destination,
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
    def test_load_config_success(self, mock_config: Mock) -> None:
        mock_instance = Mock()
        mock_config.return_value = mock_instance
        result = load_config()
        assert result == mock_instance
        mock_config.assert_called_once()

    @patch("src.main.ReplicationConfig")
    def test_load_config_validation_error(self, mock_config: Mock) -> None:
        mock_config.side_effect = PydanticValidationError.from_exception_data(
            "ReplicationConfig",
            [{"type": "missing", "loc": ("PRIMARY_SERVICEBUS_CONN",), "msg": "missing"}],
        )
        with pytest.raises(Exception):
            load_config()


class TestDynamicReplication:
    """Test dynamic topic/subscription enumeration."""

    @patch("src.main.ServiceBusAdministrationClient")
    @patch("src.main.process_subscription_messages")
    def test_topic_subscription_discovery(
        self,
        mock_process: Mock,
        mock_admin: Mock,
    ) -> None:
        mock_admin_instance = Mock()
        mock_admin.return_value = mock_admin_instance
        mock_admin_instance.list_topics.return_value = [
            Mock(name_value=t) for t in TEST_TOPICS
        ]
        mock_admin_instance.list_subscriptions.return_value = [
            Mock(subscription_name=s) for s in TEST_SUBSCRIPTIONS
        ]

        config = Mock()
        config.primary_conn_str = TEST_PRIMARY_CONN
        config.secondary_conn_str = TEST_SECONDARY_CONN
        config.replication_type = TEST_REPLICATION_TYPE

        main(Mock())
        mock_process.assert_called()


class TestSubscriptionProcessing:
    """Verify per-subscription message processing logic."""

    @patch("src.main.replicate_to_destination")
    @patch("src.main.ServiceBusClient")
    def test_no_messages(
        self,
        mock_client: Mock,
        mock_replicate: Mock,
    ) -> None:
        receiver = Mock()
        receiver.receive_messages.return_value = []
        mock_client.return_value.__enter__.return_value = mock_client
        mock_client.get_subscription_receiver.return_value = receiver

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
    def test_with_messages(
        self,
        mock_client: Mock,
        mock_replicate: Mock,
    ) -> None:
        receiver = Mock()
        msg = Mock()
        receiver.receive_messages.return_value = [msg]
        mock_client.return_value.__enter__.return_value = mock_client
        mock_client.get_subscription_receiver.return_value = receiver

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

        sender = Mock()
        client_instance = Mock()
        client_instance.get_topic_sender.return_value = sender
        mock_client.return_value.__enter__.return_value = client_instance

        replicate_to_destination(
            msg,
            TEST_SECONDARY_CONN,
            "topic-a",
            "sub-a",
            "Primary → Secondary",
            Mock(),
            Mock(),
        )

        mock_create.assert_called_once()
        sender.send_messages.assert_called_once_with(replicated)


class TestErrorCases:
    """Ensure exceptions and auth failures are handled correctly."""

    @patch("src.main.ServiceBusClient")
    def test_auth_error(self, mock_client: Mock) -> None:
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
    raise SystemExit(pytest.main([__file__]))
