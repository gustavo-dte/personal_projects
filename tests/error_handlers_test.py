"""
Unit tests for error handlers module.
"""

from unittest.mock import Mock

import pytest
from azure.core.exceptions import ClientAuthenticationError
from azure.servicebus.exceptions import ServiceBusError

from src.error_handlers import (
    handle_authentication_error,
    handle_service_bus_error,
    handle_unexpected_error,
)
from src.exceptions import ReplicationError
from src.logging_utils import log_replication_error


class TestErrorHandlers:
    """Test error handling functions."""

    def test_handle_authentication_error(self) -> None:
        """Test authentication error handling."""
        logger = Mock()
        error = ClientAuthenticationError("Authentication failed")

        try:
            handle_authentication_error(
                error=error,
                correlation_id="test-id",
                direction="Primary → Secondary",
                destination_topic="test-topic",
                logger=logger,
            )
        except ClientAuthenticationError:
            # Expected to re-raise
            pass

        logger.error.assert_called()

    def test_handle_service_bus_error(self) -> None:
        """Test Service Bus error handling."""
        logger = Mock()
        error = ServiceBusError("Service Bus error")

        try:
            handle_service_bus_error(
                error=error,
                correlation_id="test-id",
                direction="Primary → Secondary",
                destination_topic="test-topic",
                logger=logger,
            )
        except ServiceBusError:
            # Expected to re-raise
            pass

        logger.error.assert_called()

    def test_handle_unexpected_error(self) -> None:
        """Test unexpected error handling."""
        logger = Mock()
        error = RuntimeError("Unexpected error")

        with pytest.raises(ReplicationError):
            handle_unexpected_error(
                error=error,
                correlation_id="test-id",
                direction="Primary → Secondary",
                destination_topic="test-topic",
                logger=logger,
            )

        logger.error.assert_called()

    def test_log_replication_error(self) -> None:
        """Test replication error logging."""
        logger = Mock()

        log_replication_error(
            logger=logger,
            correlation_id="test-id",
            error_type="test_error",
            error_message="Test error message",
            direction="Primary → Secondary",
            destination_queue="test-queue",
        )

        logger.error.assert_called()
