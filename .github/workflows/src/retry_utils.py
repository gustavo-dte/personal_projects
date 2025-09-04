"""
Retry utilities for Service Bus replication.

This module provides retry functionality with exponential backoff
following the Twelve Factor App methodology with configurable retry parameters.
"""

import functools
import logging
import time
from typing import Any, Callable, TypeVar

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.servicebus.exceptions import ServiceBusError

from .constants import ALERT_SEVERITY_MEDIUM, ALERT_SEVERITY_HIGH
from .exceptions import ReplicationError

F = TypeVar('F', bound=Callable[..., Any])


def exponential_backoff_retry(
    max_attempts: int,
    base_delay: float,
    logger: logging.Logger
) -> Callable[[F], F]:
    """
    Decorator that implements exponential backoff retry for transient failures.
    
    This provides a configurable retry mechanism for handling transient Azure
    service failures with exponential backoff strategy.
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds, exponentially increased
        logger: Logger instance for retry logging
        
    Returns:
        Decorator function that wraps the target function with retry logic
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (ServiceRequestError, HttpResponseError, ServiceBusError) as e:
                    last_exception = e
                    if attempt < max_attempts - 1:  # Not the last attempt
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        log_retry_attempt(
                            logger=logger,
                            attempt=attempt + 1,
                            max_attempts=max_attempts,
                            delay=delay,
                            error=e
                        )
                        time.sleep(delay)
                    else:
                        # Last attempt failed
                        log_retry_exhausted(
                            logger=logger,
                            max_attempts=max_attempts,
                            final_error=e
                        )
            
            # Re-raise the last exception wrapped in ReplicationError
            if last_exception:
                correlation_id = kwargs.get('correlation_id', 'unknown')
                raise ReplicationError(
                    f"All {max_attempts} retry attempts failed: {str(last_exception)}",
                    correlation_id=correlation_id,
                    retry_count=max_attempts
                ) from last_exception
        
        return wrapper  # type: ignore
    return decorator


def log_retry_attempt(
    logger: logging.Logger,
    attempt: int,
    max_attempts: int,
    delay: float,
    error: Exception
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
    logger: logging.Logger,
    max_attempts: int,
    final_error: Exception
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
