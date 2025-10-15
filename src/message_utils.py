"""
Message processing utilities for Service Bus replication.

This module contains functions for processing and transforming Service Bus messages
during replication, following separation of concerns principle.
"""

from __future__ import annotations

import datetime
from datetime import timedelta
from typing import Any, cast

import azure.functions as func
from azure.servicebus import ServiceBusMessage

from .constants import (
    CONTENT_TYPE_BINARY,
    CONTENT_TYPE_TEXT_UTF8,
    CORRELATION_ID_PREFIX,
    PROP_ORIGINAL_MESSAGE_ID,
    PROP_REPLICATION_CORRELATION_ID,
    PROP_REPLICATION_TIMESTAMP,
)


def generate_correlation_id(source_message: func.ServiceBusMessage) -> str:
    """
    Generate or extract correlation ID for message tracking.

    Args:
        source_message: The source Service Bus message

    Returns:
        Correlation ID for tracking the replication operation
    """
    timestamp = datetime.datetime.utcnow().isoformat()
    correlation_id: str = (
        source_message.correlation_id or f"{CORRELATION_ID_PREFIX}-{timestamp}"
    )
    return correlation_id


def process_message_body(
    source_body: Any, original_content_type: str | None
) -> tuple[bytes, str]:
    """
    Process and convert message body to appropriate format for replication.

    Args:
        source_body: The original message body
        original_content_type: Original content type of the message

    Returns:
        Tuple of (processed_body_bytes, final_content_type)
    """
    if isinstance(source_body, bytes):
        # Body is already bytes - preserve as-is for maximum fidelity
        return source_body, original_content_type or CONTENT_TYPE_BINARY

    elif isinstance(source_body, str):
        # Body is string - encode to UTF-8 bytes
        processed_body = source_body.encode("utf-8")
        content_type = original_content_type or CONTENT_TYPE_TEXT_UTF8
        return processed_body, content_type

    else:
        # Handle other types by converting to string first, then bytes
        string_body = str(source_body)
        processed_body = string_body.encode("utf-8")
        content_type = original_content_type or CONTENT_TYPE_TEXT_UTF8
        return processed_body, content_type


def create_enhanced_properties(
    source_message: func.ServiceBusMessage, correlation_id: str
) -> dict[str, Any]:
    """
    Create enhanced application properties with replication metadata.

    Args:
        source_message: The source Service Bus message
        correlation_id: Correlation ID for the replication operation

    Returns:
        Dictionary of enhanced application properties
    """
    # Start with original application properties
    preserved_properties = getattr(source_message, "application_properties", {}) or {}
    enhanced_properties = preserved_properties.copy()

    # Add replication tracking metadata
    enhanced_properties[PROP_ORIGINAL_MESSAGE_ID] = source_message.message_id
    enhanced_properties[PROP_REPLICATION_CORRELATION_ID] = correlation_id
    enhanced_properties[PROP_REPLICATION_TIMESTAMP] = str(datetime.datetime.utcnow())

    return enhanced_properties


def generate_replicated_message_id(
    correlation_id: str, original_message_id: str | None
) -> str:
    """
    Generate a new message ID for the replicated message.

    Args:
        correlation_id: Correlation ID for the replication
        original_message_id: Original message ID

    Returns:
        New message ID for the replicated message
    """
    correlation_prefix = (
        correlation_id[:8] if len(correlation_id) >= 8 else correlation_id
    )

    if original_message_id:
        return f"{CORRELATION_ID_PREFIX}-{correlation_prefix}-{original_message_id}"
    else:
        return f"{CORRELATION_ID_PREFIX}-{correlation_prefix}"


def create_replicated_message(
    source_message: func.ServiceBusMessage,
    correlation_id: str,
    ttl_seconds: int | None,
) -> ServiceBusMessage:
    """
    Create a new ServiceBusMessage for replication with all properties preserved.
    """
    # --- Extract and normalize body ------------------------------------------
    if hasattr(source_message, "get_body"):
        # Legacy SDK compatibility
        source_body = source_message.get_body()
    else:
        # Modern SDK: .body is iterable of bytes
        source_body = b"".join(part for part in source_message.body)

    original_content_type = getattr(source_message, "content_type", None)
    processed_body, final_content_type = process_message_body(
        source_body, original_content_type
    )

    # --- Enhanced metadata ---------------------------------------------------
    enhanced_properties = create_enhanced_properties(source_message, correlation_id)
    new_message_id = generate_replicated_message_id(
        correlation_id, getattr(source_message, "message_id", None)
    )

    # --- TTL handling (avoid NoneType errors) -------------------------------
    msg_kwargs = dict(
        body=processed_body,
        application_properties=cast(Any, enhanced_properties),
        content_type=final_content_type,
        correlation_id=correlation_id,
        subject=getattr(source_message, "subject", None),
        session_id=getattr(source_message, "session_id", None),
        to=getattr(source_message, "to", None),
        reply_to=getattr(source_message, "reply_to", None),
        reply_to_session_id=getattr(source_message, "reply_to_session_id", None),
        partition_key=getattr(source_message, "partition_key", None),
        scheduled_enqueue_time_utc=getattr(
            source_message, "scheduled_enqueue_time_utc", None
        ),
        message_id=new_message_id,
    )

    # Only set TTL if valid and numeric
    if ttl_seconds is not None and isinstance(ttl_seconds, (int, float)):
        msg_kwargs["time_to_live"] = timedelta(seconds=int(ttl_seconds))

    # --- Construct replicated message ---------------------------------------
    return ServiceBusMessage(**msg_kwargs)
