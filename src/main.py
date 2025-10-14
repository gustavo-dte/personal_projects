import azure.functions as func
from azure.servicebus import ServiceBusClient, ServiceBusMessage, ServiceBusReceiveMode
from azure.servicebus.management import ServiceBusAdministrationClient

from .config import ReplicationConfig
from .logging_utils import configure_logger
from .message_utils import create_replicated_message
from .retry_utils import with_retry
from .error_handlers import (
    handle_replication_error,
    handle_unexpected_error,
)
from .exceptions import ReplicationError, ConfigError

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

        logger = configure_logger(config)
        logger.info(f"Running replication direction: {config.direction}")

        # ------------------------------------------------------------------
        # Create admin client to list topics and subscriptions dynamically
        # ------------------------------------------------------------------
        admin_client = ServiceBusAdministrationClient.from_connection_string(config.primary_conn_str)
        topics = [t.name for t in admin_client.list_topics()]
        app_logger.info(f"Found {len(topics)} topics: {topics}")

        for topic in topics:
            subs = [s.name for s in admin_client.list_subscriptions(topic)]
            app_logger.info(f"Found {len(subs)} subscriptions for topic '{topic}': {subs}")

            for sub in subs:
                app_logger.info(f"Processing {topic}/{sub}")
                process_subscription_messages(topic, sub, config)

        app_logger.info("✅ Replication cycle completed successfully.")

    except ConfigError as ce:
        app_logger.error(f"❌ Configuration error: {ce}")
    except Exception as e:
        app_logger.exception(f"❌ Replication cron failed: {e}")


# --------------------------------------------------------------------------
# MESSAGE PROCESSING
# --------------------------------------------------------------------------
def process_subscription_messages(topic: str, subscription: str, config: ReplicationConfig) -> None:
    """Read messages from a subscription in primary Service Bus and replicate to secondary."""
    try:
        with ServiceBusClient.from_connection_string(config.primary_conn_str) as client:
            with client.get_subscription_receiver(
                topic_name=topic,
                subscription_name=subscription,
                receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                max_wait_time=5,
            ) as receiver:

                messages = receiver.receive_messages(max_message_count=100)
                if not messages:
                    app_logger.info(f"No new messages for {topic}/{subscription}")
                    return

                app_logger.info(f"Fetched {len(messages)} messages from {topic}/{subscription}")

                for message in messages:
                    orchestrate_replication(message, config, topic)
                    receiver.complete_message(message)

    except Exception as e:
        app_logger.exception(f"Failed to process {topic}/{subscription}: {e}")


# --------------------------------------------------------------------------
# REPLICATION ORCHESTRATION
# --------------------------------------------------------------------------
def orchestrate_replication(source_message, config: ReplicationConfig, topic_name: str) -> None:
    """Replicate one message from primary to secondary (mirror topic name)."""
    dest_conn = config.secondary_conn_str
    dest_topic = topic_name
    direction = config.direction

    @with_retry(max_attempts=config.retry_config.max_attempts, base_delay=config.retry_config.base_delay)
    def send_with_retry(correlation_id=None):
        replicate_message_to_destination(source_message, dest_conn, dest_topic, config, direction, correlation_id)

    corr_id = getattr(source_message, "correlation_id", None)
    _handle_replication_exceptions(send_with_retry, corr_id, direction, dest_topic)


# --------------------------------------------------------------------------
# CORE REPLICATION
# --------------------------------------------------------------------------
def replicate_message_to_destination(source_message, dest_conn, dest_topic, config, direction, correlation_id):
    """Send one message to the secondary topic."""
    try:
        with ServiceBusClient.from_connection_string(dest_conn) as client:
            with client.get_topic_sender(topic_name=dest_topic) as sender:
                correlation_id = getattr(source_message, "correlation_id", None)
                ttl_seconds = getattr(source_message, "time_to_live", None)
                replicated_body = create_replicated_message(
                    source_message,
                    correlation_id=correlation_id,
                    ttl_seconds=ttl_seconds,
                    )
                sender.send_messages(ServiceBusMessage(replicated_body))
                _log_successful_replication(direction, dest_topic, correlation_id)
    except Exception as e:
        raise ReplicationError(f"Error sending message to {dest_topic}: {e}") from e


# --------------------------------------------------------------------------
# EXCEPTION HANDLERS
# --------------------------------------------------------------------------
def _handle_replication_exceptions(send_fn, correlation_id, direction, dest_topic):
    try:
        send_fn(correlation_id=correlation_id)
    except ReplicationError as e:
        handle_replication_error(e, correlation_id, direction, dest_topic, app_logger)
    except Exception as e:
        handle_unexpected_error(e, correlation_id, direction, dest_topic, app_logger)


def _log_successful_replication(direction, topic, correlation_id):
    msg = f"✅ Message replicated successfully ({direction}) to topic: {topic}"
    if correlation_id:
        msg += f" | Correlation ID: {correlation_id}"
    app_logger.info(msg)


# import azure.functions as func
# from azure.servicebus import ServiceBusClient, ServiceBusMessage
# import traceback

# from .config import ReplicationConfig
# from .logging_utils import configure_logger
# from .message_utils import create_replicated_message
# from .retry_utils import with_retry
# from .error_handlers import (
#     handle_servicebus_error,
#     handle_replication_error,
#     handle_unexpected_error,
# )
# from .exceptions import ReplicationError, ConfigError

# # --------------------------------------------------------------------------
# # GLOBAL LOGGER (safe even before config loads)
# # --------------------------------------------------------------------------
# app_logger = configure_logger()


# # --------------------------------------------------------------------------
# # MAIN ENTRYPOINT (timer-triggered every 5 minutes)
# # --------------------------------------------------------------------------
# def main(timer: func.TimerRequest) -> None:
#     """Timer-triggered function that replicates messages across Service Bus topics."""
#     app_logger.info("Replication cron cycle started.")
#     try:
#         # ------------------------------------------------------------------
#         # Load configuration
#         # ------------------------------------------------------------------
#         config = ReplicationConfig()
#         app_logger.info("Configuration loaded successfully.")

#         # Upgrade logger (attach AI handler if available)
#         logger = configure_logger(config)
#         logger.info(f"Running replication direction: {config.direction}")

#         # ------------------------------------------------------------------
#         # Start replication cycle
#         # ------------------------------------------------------------------
#         direction = config.direction
#         app_logger.info(f"Running replication direction: {direction}")

#         # Build a list of all topics and subscriptions dynamically
#         with ServiceBusClient.from_connection_string(config.primary_conn_str) as client:
#             mgmt_client = client.get_mgmt_client()
#             topics = [t.name for t in mgmt_client.list_topics()]

#             for topic in topics:
#                 subs = [s.subscription_name for s in mgmt_client.list_subscriptions(topic)]
#                 for sub in subs:
#                     app_logger.info(f"Processing {topic}/{sub}")
#                     process_subscription_messages(topic, sub, config)

#         app_logger.info("Replication cycle completed successfully.")

#     except ConfigError as ce:
#         app_logger.error(f"Configuration error: {ce}")
#     except Exception as e:
#         app_logger.exception(f"Replication cron failed: {e}")


# # --------------------------------------------------------------------------
# # MESSAGE PROCESSING LOGIC
# # --------------------------------------------------------------------------
# def process_subscription_messages(topic: str, subscription: str, config: ReplicationConfig) -> None:
#     """Read messages from one subscription and replicate to secondary namespace."""
#     try:
#         with ServiceBusClient.from_connection_string(config.primary_conn_str) as client:
#             with client.get_subscription_receiver(topic_name=topic, subscription_name=subscription, max_wait_time=5) as receiver:
#                 messages = receiver.receive_messages(max_message_count=100)
#                 for message in messages:
#                     orchestrate_replication(message, config, topic)
#                     receiver.complete_message(message)

#     except Exception as e:
#         app_logger.exception(f"Failed to process {topic}/{subscription}: {e}")


# # --------------------------------------------------------------------------
# # REPLICATION ORCHESTRATION
# # --------------------------------------------------------------------------
# def orchestrate_replication(source_message, config: ReplicationConfig, topic_name: str) -> None:
#     """Coordinate message replication for one topic dynamically."""
#     dest_conn = config.secondary_conn_str
#     dest_topic = topic_name  # mirror same topic name
#     direction = config.direction

#     @with_retry(max_attempts=config.retry_config.max_attempts, base_delay=config.retry_config.base_delay)
#     def send_with_retry(correlation_id=None):
#         replicate_message_to_destination(source_message, dest_conn, dest_topic, config, direction, correlation_id)

#     corr_id = getattr(source_message, "correlation_id", None)
#     _handle_replication_exceptions(send_with_retry, corr_id, direction, dest_topic)


# # --------------------------------------------------------------------------
# # CORE REPLICATION
# # --------------------------------------------------------------------------
# def replicate_message_to_destination(source_message, dest_conn, dest_topic, config, direction, correlation_id):
#     """Send one message to the secondary topic."""
#     try:
#         with ServiceBusClient.from_connection_string(dest_conn) as client:
#             with client.get_topic_sender(topic_name=dest_topic) as sender:
#                 replicated = create_replicated_message(source_message)
#                 sender.send_messages(ServiceBusMessage(replicated))
#                 _log_successful_replication(direction, dest_topic, correlation_id)

#     except Exception as e:
#         raise ReplicationError(f"Error sending message to {dest_topic}: {e}") from e


# # --------------------------------------------------------------------------
# # HELPER HANDLERS
# # --------------------------------------------------------------------------
# def _handle_replication_exceptions(send_fn, correlation_id, direction, dest_topic):
#     """Standardized exception handling with retries and categorized errors."""
#     try:
#         send_fn(correlation_id=correlation_id)
#     except ReplicationError as e:
#         handle_replication_error(e, correlation_id, direction, dest_topic, app_logger)
#     except Exception as e:
#         handle_unexpected_error(e, correlation_id, direction, dest_topic, app_logger)


# def _log_successful_replication(direction, topic, correlation_id):
#     """Log a successful replication event."""
#     msg = f"Message replicated successfully ({direction}) to topic: {topic}"
#     if correlation_id:
#         msg += f" | Correlation ID: {correlation_id}"
#     app_logger.info(msg)
