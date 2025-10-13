"""
Message processing utilities for Service Bus replication.

This module contains functions for processing and transforming Service Bus messages
during replication, following separation of concerns principle.
"""

from __future__ import annotations

import datetime
from typing import Any, cast

import azure.functions as func
from azure.servicebus import ServiceBusMessage
from azure.servicebus.management import ServiceBusAdministrationClient
from .exceptions import ReplicationError

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


def create_replicated_message(source_message, correlation_id, ttl_seconds):
    """Create a new ServiceBusMessage based on a received message."""
    try:
        # ✅ Modern SDK body extraction
        if hasattr(source_message, "body"):
            body_bytes = b"".join(source_message.body)
        else:
            # backward compatibility (very old SDKs)
            body_bytes = source_message.get_body()

        body_str = body_bytes.decode("utf-8") if isinstance(body_bytes, (bytes, bytearray)) else str(body_bytes)

        msg = ServiceBusMessage(
            body=body_str,
            content_type=getattr(source_message, "content_type", "application/json"),
            subject=getattr(source_message, "subject", None),
            correlation_id=correlation_id,
            time_to_live=ttl_seconds,
        )
        return msg
    except Exception as e:
        raise ReplicationError(f"Failed to create replicated message: {e}")

def list_topics_and_subscriptions(conn_str: str) -> dict[str, list[str]]:
    """
    List all topics and their subscriptions in the Service Bus namespace.
    Args:
        conn_str: Connection string for the Service Bus namespace
    Returns:
        Dictionary mapping topic names to lists of subscription names
    """
    client = ServiceBusAdministrationClient.from_connection_string(conn_str)
    result = {}
    for topic in client.list_topics():
        subs = [s.subscription_name for s in client.list_subscriptions(topic.name)]
        result[topic.name] = subs
    return result
