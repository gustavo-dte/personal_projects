"""
Unit tests for exceptions module.
"""

import pytest

from src.exceptions import ConfigError, ReplicationError


class TestExceptions:
    """Test custom exception classes."""

    def test_config_error_creation(self) -> None:
        """Test ConfigError can be created with a message."""
        message = "Configuration is invalid"
        error = ConfigError(message)
        
        assert str(error) == message
        assert isinstance(error, Exception)

    def test_config_error_raise_and_catch(self) -> None:
        """Test ConfigError can be raised and caught."""
        with pytest.raises(ConfigError, match="Test config error"):
            raise ConfigError("Test config error")

    def test_replication_error_creation(self) -> None:
        """Test ReplicationError can be created with a message."""
        message = "Replication failed"
        error = ReplicationError(message)
        
        assert str(error) == message
        assert isinstance(error, Exception)

    def test_replication_error_raise_and_catch(self) -> None:
        """Test ReplicationError can be raised and caught."""
        with pytest.raises(ReplicationError, match="Test replication error"):
            raise ReplicationError("Test replication error")

    def test_replication_error_with_cause(self) -> None:
        """Test ReplicationError can be chained with another exception."""
        original_error = ValueError("Original error")
        
        with pytest.raises(ReplicationError) as exc_info:
            try:
                raise original_error
            except ValueError as e:
                raise ReplicationError("Replication failed") from e
        
        assert exc_info.value.__cause__ == original_error