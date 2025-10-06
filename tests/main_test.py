"""
Unit tests for the improved Service Bus replication function.

These tests demonstrate how the refactored code is now easily testable
with proper separation of concerns and isolated functions.
"""

import logging
from unittest.mock import Mock, patch

import pytest
from azure.core.exceptions import (
    ClientAuthenticationError,
    ServiceRequestError,
)
from pydantic import ValidationError as PydanticValidationError

from src.shared.config import DeadLetterConfig, ReplicationConfig, RetryConfig
from src.shared.constants import (
    DEFAULT_DELTA_MINUTES,
    DEFAULT_RTO_MINUTES,
    DIRECTION_PRIMARY_TO_SECONDARY,
    REPLICATION_TYPE_PRIMARY_TO_SECONDARY,
)
from src.shared.exceptions import ConfigError, ReplicationError, ValidationError
from src.shared.main import (
    handle_authentication_error,
    load_and_validate_config,
    orchestrate_replication,
    send_message_to_destination,
)
from src.shared.message_utils import (
    create_enhanced_properties,
    generate_correlation_id,
    generate_replicated_message_id,
    process_message_body,
)
from src.shared.retry_utils import exponential_backoff_retry
from tests.constants_test import TEST_SERVICEBUS_CONNECTION_STRING


class TestConfigurationLoading:
    """Test configuration loading and validation."""

    @patch("src.shared.main.ReplicationConfig")
    def test_load_and_validate_config_success(self, mock_config_class: Mock) -> None:
        """Test successful configuration loading."""
        mock_config = Mock()
        mock_config.replication_type = REPLICATION_TYPE_PRIMARY_TO_SECONDARY
        mock_config_class.return_value = mock_config

        result = load_and_validate_config()

        assert result == mock_config
        mock_config_class.assert_called_once()

    @patch("src.shared.main.ReplicationConfig")
    def test_load_and_validate_config_validation_error(
        self, mock_config_class: Mock
    ) -> None:
        """Test configuration loading with validation error."""
        mock_config_class.side_effect = PydanticValidationError.from_exception_data(
            "TestModel",
            [{"type": "missing", "loc": ("field",), "msg": "Field required"}],
        )

        with pytest.raises(ConfigError) as exc_info:
            load_and_validate_config()

        assert "Configuration validation failed" in str(exc_info.value)

    @patch("src.shared.main.ReplicationConfig")
    def test_load_and_validate_config_unexpected_error(
        self, mock_config_class: Mock
    ) -> None:
        """Test configuration loading with unexpected error."""
        mock_config_class.side_effect = RuntimeError("Unexpected error")

        with pytest.raises(ConfigError) as exc_info:
            load_and_validate_config()

        assert "Unexpected error loading configuration" in str(exc_info.value)


class TestMessageUtils:
    """Test message utility functions."""

    def test_generate_correlation_id_existing(self) -> None:
        """Test correlation ID generation when message already has one."""
        mock_message = Mock()
        mock_message.correlation_id = "existing-id"

        result = generate_correlation_id(mock_message)

        assert result == "existing-id"

    def test_generate_correlation_id_new(self) -> None:
        """Test correlation ID generation for new message."""
        mock_message = Mock()
        mock_message.correlation_id = None

        result = generate_correlation_id(mock_message)

        assert result.startswith("repl-")


class TestRetryUtils:
    """Test retry utility functions."""

    def test_exponential_backoff_retry_success(self) -> None:
        """Test successful execution without retries."""
        logger = Mock()
        mock_func = Mock(return_value="success")
        decorated = exponential_backoff_retry(
            max_attempts=3, base_delay=0.1, logger=logger
        )(mock_func)

        result = decorated()

        assert result == "success"
        mock_func.assert_called_once()
        logger.info.assert_not_called()

    @patch("src.shared.retry_utils.time.sleep")
    def test_exponential_backoff_retry_with_retries(self, mock_sleep: Mock) -> None:
        """Test retry behavior with temporary failures."""
        logger = Mock()
        mock_func = Mock(
            side_effect=[
                ServiceRequestError("error"),
                ServiceRequestError("error"),
                "success",
            ]
        )
        decorated = exponential_backoff_retry(
            max_attempts=3, base_delay=0.1, logger=logger
        )(mock_func)

        result = decorated(correlation_id="test-id")

        assert result == "success"
        assert mock_func.call_count == 3
        assert logger.warning.call_count == 2
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(0.1)  # First retry delay
        mock_sleep.assert_any_call(0.2)  # Second retry delay

    @patch("src.shared.retry_utils.time.sleep")
    def test_exponential_backoff_retry_exhausted(self, mock_sleep: Mock) -> None:
        """Test behavior when all retries are exhausted."""
        logger = Mock()
        error = ServiceRequestError("persistent error")
        mock_func = Mock(side_effect=error)
        decorated = exponential_backoff_retry(
            max_attempts=3, base_delay=0.1, logger=logger
        )(mock_func)

        with pytest.raises(ReplicationError) as exc_info:
            decorated(correlation_id="test-id")

        assert "All 3 retry attempts failed" in str(exc_info.value)
        assert mock_func.call_count == 3
        assert logger.warning.call_count == 2
        logger.error.assert_called()
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(0.1)  # First retry delay
        mock_sleep.assert_any_call(0.2)  # Second retry delay

    def test_process_message_body_bytes(self) -> None:
        """Test processing message body that is already bytes."""
        body = b"test message"
        content_type = "application/json"

        processed_body, final_content_type = process_message_body(body, content_type)

        assert processed_body == body
        assert final_content_type == content_type

    def test_process_message_body_string(self) -> None:
        """Test processing message body that is a string."""
        body = "test message"
        content_type = None

        processed_body, final_content_type = process_message_body(body, content_type)

        assert processed_body == b"test message"
        assert final_content_type == "text/plain; charset=utf-8"

    def test_process_message_body_other_type(self) -> None:
        """Test processing message body of other types."""
        body = 12345
        content_type = None

        processed_body, final_content_type = process_message_body(body, content_type)

        assert processed_body == b"12345"
        assert final_content_type == "text/plain; charset=utf-8"

    def test_create_enhanced_properties(self) -> None:
        """Test creation of enhanced properties with replication metadata."""
        mock_message = Mock()
        mock_message.application_properties = {"original_prop": "value"}
        mock_message.message_id = "original-id"
        correlation_id = "test-correlation-id"

        result = create_enhanced_properties(mock_message, correlation_id)

        assert result["original_prop"] == "value"
        assert result["x-original-message-id"] == "original-id"
        assert result["x-replication-correlation-id"] == correlation_id
        assert "x-replication-timestamp" in result

    def test_generate_replicated_message_id_with_original(self) -> None:
        """Test generation of replicated message ID with original ID."""
        correlation_id = "test-correlation-id"
        original_id = "original-message-id"

        result = generate_replicated_message_id(correlation_id, original_id)

        assert result == "repl-test-cor-original-message-id"

    def test_generate_replicated_message_id_without_original(self) -> None:
        """Test generation of replicated message ID without original ID."""
        correlation_id = "test-correlation-id"
        original_id = None

        result = generate_replicated_message_id(correlation_id, original_id)

        assert result == "repl-test-cor"


class TestErrorHandling:
    """Test error handling functions."""

    def test_handle_authentication_error(self) -> None:
        """Test handling of authentication errors."""
        error = ClientAuthenticationError("Auth failed")
        correlation_id = "test-id"
        direction = DIRECTION_PRIMARY_TO_SECONDARY
        destination_queue = "test-queue"

        # Create a logger for testing
        logger = logging.getLogger("test-logger")

        with pytest.raises(ClientAuthenticationError) as exc_info:
            handle_authentication_error(
                error, correlation_id, direction, destination_queue, logger
            )

        assert "Failed to authenticate with Service Bus" in str(exc_info.value)


class TestReplicationOrchestration:
    """Test replication orchestration functions."""

    @patch("src.shared.main.replicate_message_to_destination")
    def test_orchestrate_replication_success(self, mock_replicate: Mock) -> None:
        """Test successful replication orchestration."""
        mock_message = Mock()
        mock_config = Mock()
        mock_config.get_destination_config.return_value = (
            "conn_str",
            "queue_name",
            DIRECTION_PRIMARY_TO_SECONDARY,
        )
        mock_config.ttl_seconds = 600
        mock_config.retry_config.max_attempts = 3
        mock_config.retry_config.base_delay = 1.0

        orchestrate_replication(mock_message, mock_config)

        mock_replicate.assert_called_once()
        call_args = mock_replicate.call_args
        assert call_args[1]["source_message"] == mock_message
        assert call_args[1]["destination_connection_string"] == "conn_str"
        assert call_args[1]["destination_topic_name"] == "queue_name"

    def test_orchestrate_replication_validation_error(self) -> None:
        """Test replication orchestration with validation error."""
        mock_message = Mock()
        mock_config = Mock()
        mock_config.get_destination_config.side_effect = ValidationError(
            "Invalid config"
        )

        with pytest.raises(ValidationError):
            orchestrate_replication(mock_message, mock_config)


class TestReplicationConfig:
    """Test Pydantic configuration model."""

    def test_config_creation_valid(self) -> None:
        """Test creation of valid configuration."""
        config_data = {
            "REPLICATION_TYPE": REPLICATION_TYPE_PRIMARY_TO_SECONDARY,
            "SECONDARY_SERVICEBUS_CONN": TEST_SERVICEBUS_CONNECTION_STRING,
            "SECONDARY_TOPIC_NAME": "test-queue",
            "RTO_MINUTES": DEFAULT_RTO_MINUTES,
            "DELTA_MINUTES": DEFAULT_DELTA_MINUTES,
        }

        config = ReplicationConfig(**config_data)

        assert config.replication_type == REPLICATION_TYPE_PRIMARY_TO_SECONDARY
        assert config.secondary_conn_str == TEST_SERVICEBUS_CONNECTION_STRING
        assert config.secondary_queue == "test-queue"
        assert isinstance(config.retry_config, RetryConfig)
        assert isinstance(config.dead_letter_config, DeadLetterConfig)

    def test_config_ttl_seconds_calculation(self) -> None:
        """Test TTL seconds calculation."""
        config_data = {
            "REPLICATION_TYPE": REPLICATION_TYPE_PRIMARY_TO_SECONDARY,
            "SECONDARY_SERVICEBUS_CONN": TEST_SERVICEBUS_CONNECTION_STRING,
            "SECONDARY_TOPIC_NAME": "test-queue",
            "RTO_MINUTES": 10,
            "DELTA_MINUTES": 2,
        }

        config = ReplicationConfig(**config_data)

        assert config.ttl_seconds == 720  # (10 + 2) * 60

    def test_config_direction_property(self) -> None:
        """Test direction property formatting."""
        config_data = {
            "REPLICATION_TYPE": REPLICATION_TYPE_PRIMARY_TO_SECONDARY,
            "SECONDARY_SERVICEBUS_CONN": TEST_SERVICEBUS_CONNECTION_STRING,
            "SECONDARY_TOPIC_NAME": "test-queue",
        }

        config = ReplicationConfig(**config_data)

        assert config.direction == DIRECTION_PRIMARY_TO_SECONDARY

    def test_config_get_destination_config(self) -> None:
        """Test getting destination configuration."""
        config_data = {
            "REPLICATION_TYPE": REPLICATION_TYPE_PRIMARY_TO_SECONDARY,
            "SECONDARY_SERVICEBUS_CONN": TEST_SERVICEBUS_CONNECTION_STRING,
            "SECONDARY_TOPIC_NAME": "test-queue",
        }

        config = ReplicationConfig(**config_data)
        conn_str, queue_name, direction = config.get_destination_config()

        assert conn_str == TEST_SERVICEBUS_CONNECTION_STRING
        assert queue_name == "test-queue"
        assert direction == DIRECTION_PRIMARY_TO_SECONDARY


# Integration test example
class TestIntegration:
    """Integration tests for the complete replication flow."""

    @patch("src.shared.main.ServiceBusClient")
    @patch("src.shared.main.create_replicated_message")
    def test_send_message_to_destination_integration(
        self, mock_create_msg: Mock, mock_client_class: Mock
    ) -> None:
        """Test the complete message sending flow."""
        # Setup mocks
        mock_client = Mock()
        mock_sender = Mock()

        # Mock the context manager properly
        mock_sender_context = Mock()
        mock_sender_context.__enter__ = Mock(return_value=mock_sender)
        mock_sender_context.__exit__ = Mock(return_value=False)
        mock_client.get_topic_sender.return_value = mock_sender_context

        mock_client_context = Mock()
        mock_client_context.__enter__ = Mock(return_value=mock_client)
        mock_client_context.__exit__ = Mock(return_value=False)
        mock_client_class.from_connection_string.return_value = mock_client_context

        mock_message = Mock()

        # Execute
        send_message_to_destination(
            destination_connection_string="test_conn_str",
            destination_topic_name="test_queue",
            message=mock_message,
            correlation_id="test_id",
        )

        # Verify
        mock_client_class.from_connection_string.assert_called_once_with(
            "test_conn_str"
        )
        mock_client.get_topic_sender.assert_called_once_with(topic_name="test_queue")
        mock_sender.send_messages.assert_called_once_with(mock_message)


if __name__ == "__main__":
    pytest.main([__file__])
