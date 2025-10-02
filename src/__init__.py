import logging
import azure.functions as func

from shared.config import settings
from shared.main import orchestrate_replication
from shared.exceptions import ConfigError


def main(msg1: func.ServiceBusMessage = None, msg2: func.ServiceBusMessage = None) -> None:
    logger = logging.getLogger("replication_function")

    try:
        logger.info("Replication function triggered")
        config = settings  # already loaded from env vars

        # Gather the incoming messages from both bindings
        incoming_messages = [msg for msg in [msg1, msg2] if msg is not None]

        if not incoming_messages:
            logger.warning("No messages received on any subscription binding")
            return

        # Loop over all received messages
        for msg in incoming_messages:
            try:
                # Log which subscription it came from
                logger.info(
                    f"Processing message from topic={config.primary_queue} "
                    f"subscription={msg.metadata.get('SystemProperties', {}).get('SubscriptionName', 'unknown')}"
                )

                # Call orchestrator
                orchestrate_replication(
                    source_message=msg,
                    replication_config=config
                )
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)

        # Optionally: loop through SUBSCRIPTION_LIST to log / monitor configured subs
        if config.subscription_list:
            logger.info(f"Configured subscriptions: {config.subscription_list}")

    except ConfigError as ce:
        logger.critical(f"Configuration error: {ce}", exc_info=True)
        raise
    except Exception as e:
        logger.critical(f"Unhandled error in replication function: {e}", exc_info=True)
        raise
