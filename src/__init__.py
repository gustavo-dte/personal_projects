import os
import logging
import azure.functions as func
from azure.servicebus import ServiceBusClient
from .replication_handler import orchestrate_replication, load_replication_config

logger = logging.getLogger("replication_function")

TOPIC_NAME = os.getenv("PRIMARY_TOPIC_NAME")
CONN_STR = os.getenv("PRIMARY_SERVICEBUS_CONN")
SUBS_LIST = [s.strip() for s in os.getenv("SUBSCRIPTION_LIST", "").split(",") if s.strip()]

def main(msg1: func.ServiceBusMessage = None, msg2: func.ServiceBusMessage = None):
    config = load_replication_config()

    # Figure out which trigger fired
    trigger_msg = msg1 or msg2
    if trigger_msg:
        try:
            logger.info("Processing triggered message first...")
            orchestrate_replication(source_message=trigger_msg, replication_config=config)
        except Exception as e:
            logger.error(f"Error processing triggered message: {e}")

    # Loop across all configured subscriptions (from env var)
    try:
        with ServiceBusClient.from_connection_string(CONN_STR) as client:
            for sub in SUBS_LIST:
                logger.info(f"Checking subscription {sub} for messages...")
                receiver = client.get_subscription_receiver(
                    topic_name=TOPIC_NAME,
                    subscription_name=sub,
                    max_wait_time=5
                )
                with receiver:
                    for sb_msg in receiver.receive_messages(max_message_count=10):
                        try:
                            logger.info(f"Processing message from {sub}")
                            orchestrate_replication(source_message=sb_msg, replication_config=config)
                            receiver.complete_message(sb_msg)
                        except Exception as e:
                            logger.error(f"Error in subscription {sub}: {e}")
                            receiver.abandon_message(sb_msg)
    except Exception as e:
        logger.error(f"Error looping across subscriptions: {e}")
        raise
