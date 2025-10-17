"""
Unit tests for retry utilities module.
"""

from typing import cast
from unittest.mock import Mock, patch

import pytest

from src.retry_utils import with_retry


class TestRetryUtils:
    """Test retry utility functions."""

    def test_with_retry_success_first_attempt(self) -> None:
        """Test that successful function calls don't retry."""
        mock_func = Mock(return_value="success")

        @with_retry(max_attempts=3, base_delay=0.1)
        def test_func() -> str:
            return cast(str, mock_func())

        result = test_func()

        assert result == "success"
        assert mock_func.call_count == 1

    def test_with_retry_success_after_failures(self) -> None:
        """Test that function succeeds after some failures."""
        mock_func = Mock()
        # Fail twice, then succeed
        mock_func.side_effect = [Exception("fail1"), Exception("fail2"), "success"]

        @with_retry(max_attempts=3, base_delay=0.01)  # Very short delay for testing
        def test_func() -> str:
            return cast(str, mock_func())

        result = test_func()

        assert result == "success"
        assert mock_func.call_count == 3

    def test_with_retry_all_attempts_fail(self) -> None:
        """Test that function re-raises after all attempts fail."""
        mock_func = Mock()
        mock_func.side_effect = Exception("persistent failure")

        @with_retry(max_attempts=2, base_delay=0.01)
        def test_func() -> str:
            return cast(str, mock_func())

        with pytest.raises(Exception, match="persistent failure"):
            test_func()

        assert mock_func.call_count == 2

    @patch("src.retry_utils.time.sleep")
    def test_with_retry_delay_calculation(self, mock_sleep: Mock) -> None:
        """Test that retry delays are calculated correctly."""
        mock_func = Mock()
        mock_func.side_effect = [Exception("fail"), "success"]

        @with_retry(max_attempts=2, base_delay=1.0)
        def test_func() -> str:
            return cast(str, mock_func())

        result = test_func()

        assert result == "success"
        # Should have slept for the base delay
        mock_sleep.assert_called_once_with(1.0)
