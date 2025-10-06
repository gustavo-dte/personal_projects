"""Service Bus replication function package."""

import azure.functions as func

from shared.logging_utils import configure_logger
from shared.main import (
    configure_application_logging,
    load_and_validate_config,
    orchestrate_replication,
)

# Temporary logger until we fully migrate to shared.logging_utils
app_logger = configure_logger()


def main(msg: func.ServiceBusMessage) -> None:
    """
    Azure Function entry point for Service Bus replication.
    """
    app_logger.info("Replication function triggered.")

    try:
        # Load and validate configuration
        config = load_and_validate_config()

        # Reconfigure logger with application settings
        logger = configure_application_logging(config)

        # Orchestrate replication process
        orchestrate_replication(source_message=msg, replication_config=config)

        logger.info("Replication function executed successfully.")

    except Exception as e:
        app_logger.error(f"An error occurred in the replication function: {e}")
        raise
