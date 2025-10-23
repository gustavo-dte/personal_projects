"""
Unit tests for message utilities module.
"""

from unittest.mock import Mock

from src.ServiceBusReplication.constants import CORRELATION_ID_PREFIX
from src.ServiceBusReplication.message_utils import (
    create_enhanced_properties,
    generate_correlation_id,
    process_message_body,
)


class TestMessageUtils:
    """Test message utility functions."""

    def test_generate_correlation_id_with_existing_id(self) -> None:
        """Test generating correlation ID when message already has one."""
        msg = Mock()
        msg.correlation_id = "existing-id"

        result = generate_correlation_id(msg)
        assert result == "existing-id"

    def test_generate_correlation_id_without_existing_id(self) -> None:
        """Test generating correlation ID when message doesn't have one."""
        msg = Mock()
        msg.correlation_id = None

        result = generate_correlation_id(msg)
        assert result.startswith(CORRELATION_ID_PREFIX)

    def test_process_message_body_bytes(self) -> None:
        """Test processing message body that's already bytes."""
        body = b"test message"
        content_type = "application/octet-stream"

        processed_body, final_content_type = process_message_body(body, content_type)

        assert processed_body == body
        assert final_content_type == content_type

    def test_process_message_body_string(self) -> None:
        """Test processing message body that's a string."""
        body = "test message"
        content_type = "text/plain"

        processed_body, final_content_type = process_message_body(body, content_type)

        assert processed_body == b"test message"
        assert final_content_type == content_type

    def test_create_enhanced_properties(self) -> None:
        """Test creating enhanced properties for a message."""
        msg = Mock()
        msg.message_id = "test-msg-id"
        msg.application_properties = {"key": "value"}

        correlation_id = "test-correlation-id"

        result = create_enhanced_properties(msg, correlation_id)

        assert isinstance(result, dict)
        assert "key" in result  # Original properties preserved
