import logging
from typing import Any, Optional

import azure.functions as func
from azure.servicebus import ServiceBusClient
from azure.servicebus.management import ServiceBusAdministrationClient

from src.exceptions import ConfigError, ReplicationError

from .config import ReplicationConfig
from .error_handlers import (
    handle_unexpected_error,
)
from .logging_utils import configure_logger
from .message_utils import create_replicated_message
from .retry_utils import with_retry

# --------------------------------------------------------------------------
# GLOBAL LOGGER
# --------------------------------------------------------------------------
app_logger = configure_logger()


# --------------------------------------------------------------------------
# MAIN ENTRYPOINT (Timer Trigger)
# --------------------------------------------------------------------------
def main(timer: func.TimerRequest) -> None:
    """Timer-triggered function that replicates messages across Service Bus topics."""
    app_logger.info("Replication cron cycle started.")
    try:
        config = ReplicationConfig()
        app_logger.info("✅ Configuration loaded successfully.")
        app_logger.info(f"Running replication direction: {config.direction}")

        # ------------------------------------------------------------------
        # Create admin client to list topics and subscriptions dynamically
        # ------------------------------------------------------------------
        with ServiceBusClient.from_connection_string(
            config.primary_conn_str
        ) as source_client:
            admin_client = ServiceBusAdministrationClient.from_connection_string(
                config.primary_conn_str
            )
            topics = [t.name for t in admin_client.list_topics()]
            app_logger.info(f"Found {len(topics)} topics: {topics}")

            for topic in topics:
                subs = [s.name for s in admin_client.list_subscriptions(topic)]
                app_logger.info(
                    f"Found {len(subs)} subscriptions for topic '{topic}': {subs}"
                )

                for sub in subs:
                    app_logger.info(f"Processing {topic}/{sub}")
                    process_subscription_messages(
                        client=source_client,
                        topic=topic,
                        subscription=sub,
                        dest_conn=config.secondary_conn_str,
                        direction="Primary → Secondary",
                        logger=app_logger,
                    )

        app_logger.info("✅ Replication cycle completed successfully.")

    except ConfigError as ce:
        app_logger.error(f"❌ Configuration error: {ce}")
    except Exception as e:
        app_logger.exception(f"❌ Replication cron failed: {e}")


# --------------------------------------------------------------------------
# MESSAGE PROCESSING
# --------------------------------------------------------------------------
def process_subscription_messages(
    client: ServiceBusClient, 
    topic: str, 
    subscription: str, 
    dest_conn: str, 
    direction: str, 
    logger: logging.Logger
) -> None:
    """Read messages from one subscription and replicate them safely."""

    with client.get_subscription_receiver(
        topic_name=topic, subscription_name=subscription, max_wait_time=5
    ) as receiver:
        messages = receiver.receive_messages(max_message_count=10)
        if not messages:
            logger.info(f"No new messages for {topic}/{subscription}")
            return

        logger.info(f"🔁 Found {len(messages)} messages in {topic}/{subscription}")

        for msg in messages:
            correlation_id = getattr(msg, "correlation_id", None) or "replica"
            ttl_seconds = getattr(msg, "time_to_live", None)

            try:
                # Create replicated copy
                replicated = create_replicated_message(
                    msg, correlation_id=correlation_id, ttl_seconds=ttl_seconds
                )

                # Send to destination
                with ServiceBusClient.from_connection_string(dest_conn) as dest_client:
                    with dest_client.get_topic_sender(topic_name=topic) as sender:
                        sender.send_messages(replicated)

                # Complete only after successful send
                receiver.complete_message(msg)
                logger.info(
                    "✅ Replicated message %s from %s/%s",
                    correlation_id,
                    topic,
                    subscription,
                )


            except Exception as e:
                # Log & abandon to retry later
                receiver.abandon_message(msg)
                logger.error(
                    "❌ Failed to replicate message %s from %s/%s: %s",
                    correlation_id,
                    topic,
                    subscription,
                    e,
                )



# --------------------------------------------------------------------------
# REPLICATION ORCHESTRATION
# --------------------------------------------------------------------------
def orchestrate_replication(
    source_message: func.ServiceBusMessage, config: ReplicationConfig, topic_name: str
) -> None:
    """Replicate one message from primary to secondary (mirror topic name)."""
    dest_conn = config.secondary_conn_str
    dest_topic = topic_name
    direction = config.direction

    @with_retry(
        max_attempts=config.retry_config.max_attempts,
        base_delay=config.retry_config.base_delay,
    )
    def send_with_retry(correlation_id: str) -> None:
        replicate_message_to_destination(
            source_message, dest_conn, dest_topic, direction, correlation_id
        )

    corr_id = getattr(source_message, "correlation_id", None) or "replica"
    _handle_replication_exceptions(send_with_retry, corr_id, direction, dest_topic)


# --------------------------------------------------------------------------
# CORE REPLICATION
# --------------------------------------------------------------------------
def replicate_message_to_destination(
    source_message: func.ServiceBusMessage, 
    dest_conn: str, 
    dest_topic: str, 
    direction: str, 
    correlation_id: str
) -> None:
    """Send one message to the secondary topic."""
    try:
        with ServiceBusClient.from_connection_string(dest_conn) as client:
            with client.get_topic_sender(topic_name=dest_topic) as sender:
                ttl_seconds = getattr(source_message, "time_to_live", None)

                # ✅ create_replicated_message already returns a ServiceBusMessage
                replicated_message = create_replicated_message(
                    source_message,
                    correlation_id=correlation_id,
                    ttl_seconds=ttl_seconds,
                )

                # ✅ send directly, don’t wrap again
                sender.send_messages(replicated_message)

                _log_successful_replication(direction, dest_topic, correlation_id)

    except Exception as e:
        raise ReplicationError(f"Error sending message to {dest_topic}: {e}") from e


# --------------------------------------------------------------------------
# EXCEPTION HANDLERS
# --------------------------------------------------------------------------
def _handle_replication_exceptions(
    send_fn: Any, 
    correlation_id: str, 
    direction: str, 
    dest_topic: str
) -> None:
    try:
        send_fn(correlation_id=correlation_id)
    except Exception as e:
        handle_unexpected_error(e, correlation_id, direction, dest_topic, app_logger)


def _log_successful_replication(direction: str, topic: str, correlation_id: str) -> None:
    msg = f"✅ Message replicated successfully ({direction}) to topic: {topic}"
    msg += f" | Correlation ID: {correlation_id}"
    app_logger.info(msg)
