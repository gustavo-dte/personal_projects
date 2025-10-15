"""
Retry utilities for Service Bus replication.

This module provides retry functionality with exponential backoff
following the Twelve Factor App methodology with configurable retry parameters.
"""

import functools
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar

from .constants import ALERT_SEVERITY_HIGH, ALERT_SEVERITY_MEDIUM

F = TypeVar("F", bound=Callable[..., Any])


def with_retry(max_attempts: int = 3, base_delay: float = 1.0, backoff_factor: float = 2.0) -> Callable[[F], F]:
    """
    Decorator for retrying a function if it raises an exception.
    Args:
        max_attempts (int): Maximum number of attempts before giving up.
        base_delay (float): Initial delay between retries (in seconds).
        backoff_factor (float): Multiplier applied to delay after each failure.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = logging.getLogger(func.__module__)
            attempt = 1
            delay = base_delay

            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Retry failed after {max_attempts} attempts: {e}")
                        raise
                    logger.warning(
                        f"Attempt {attempt} failed: {e}. Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                    delay *= backoff_factor
                    attempt += 1

        return wrapper  # type: ignore

    return decorator


def log_retry_attempt(
    logger: logging.Logger,
    attempt: int,
    max_attempts: int,
    delay: float,
    error: Exception,
) -> None:
    """
    Log retry attempt information.

    Args:
        logger: Logger instance
        attempt: Current attempt number
        max_attempts: Maximum number of attempts
        delay: Delay before next retry in seconds
        error: Exception that triggered the retry
    """
    logger.warning(
        "Transient error on attempt %d, retrying in %ss",
        attempt,
        delay,
        extra={
            "attempt": attempt,
            "max_attempts": max_attempts,
            "delay_seconds": delay,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "alert_severity": ALERT_SEVERITY_MEDIUM,
        },
    )


def log_retry_exhausted(
    logger: logging.Logger, max_attempts: int, final_error: Exception
) -> None:
    """
    Log when all retry attempts are exhausted.

    Args:
        logger: Logger instance
        max_attempts: Maximum number of attempts that were made
        final_error: The final exception that caused failure
    """
    logger.error(
        "All %d retry attempts failed",
        max_attempts,
        extra={
            "max_attempts": max_attempts,
            "final_error_type": type(final_error).__name__,
            "final_error_message": str(final_error),
            "alert_severity": ALERT_SEVERITY_HIGH,
        },
    )
