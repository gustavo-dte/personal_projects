import datetime
import logging

import azure.functions as func
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceNotFoundError,
)
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus.exceptions import ServiceBusError

from .config import ReplicationConfig


class ReplicationConfigurationError(Exception):
    """Custom exception raised when there's an issue with replication configuration."""


def replicate_message(
    *,
    source_message: func.ServiceBusMessage,
    destination_connection_string: str,
    destination_queue_name: str,
    ttl_seconds: int,
    direction: str
) -> None:
    """
    Replicates a Service Bus message to the destination queue.
    
    This function handles the actual message replication logic. We use keyword-only
    arguments to make the function calls more explicit and reduce the chance of
    parameter mix-ups.

    Args:
        source_message: The original Service Bus message that needs to be replicated
        destination_connection_string: Connection string for the destination Service Bus
        destination_queue_name: Name of the queue where the message should be replicated
        ttl_seconds: How long the replicated message should live (in seconds)
        direction: A human-friendly description of the replication direction for logs

    Raises:
        Various Azure exceptions depending on what goes wrong during replication
    """
    logging.debug(f"Starting message replication to {direction}")
    
    try:
        # Create the Service Bus client using the destination connection string
        with ServiceBusClient.from_connection_string(
            destination_connection_string
        ) as client:
            # Get a sender for the specific queue
            queue_sender = client.get_queue_sender(queue_name=destination_queue_name)
            
            with queue_sender:
                # Set up the TTL for the new message
                message_ttl = datetime.timedelta(seconds=ttl_seconds)
                
                # Create a new message with the same body and properties
                replicated_message = ServiceBusMessage(
                    source_message.get_body(),
                    time_to_live=message_ttl,
                    application_properties=getattr(
                        source_message, "application_properties", None
                    ),
                )
                
                # Send the message to the destination queue
                queue_sender.send_messages(replicated_message)
                
                logging.info(f"Successfully replicated message to {direction}")

    except ClientAuthenticationError as auth_error:
        error_message = f"Failed to authenticate with Service Bus: {auth_error}"
        logging.error(error_message)
        raise ClientAuthenticationError(error_message) from auth_error

    except ResourceNotFoundError as resource_error:
        error_message = (
            f"Could not find destination queue '{destination_queue_name}': "
            f"{resource_error}"
        )
        logging.error(error_message)
        raise ResourceNotFoundError(error_message) from resource_error

    except ServiceBusError as sb_error:
        error_message = f"Service Bus operation failed: {sb_error}"
        logging.error(error_message)
        raise ServiceBusError(error_message) from sb_error

    except HttpResponseError as http_error:
        error_message = f"HTTP request failed during message replication: {http_error}"
        logging.error(error_message)
        raise HttpResponseError(error_message) from http_error

    except Exception as unexpected_error:
        # This catches anything we didn't anticipate - always good to have a fallback
        error_message = (
            f"Unexpected error occurred during message replication: "
            f"{unexpected_error}"
        )
        logging.error(error_message)
        raise RuntimeError(error_message) from unexpected_error


def main(msg: func.ServiceBusMessage) -> None:
    """
    Main entry point for the Azure Function.
    
    This function gets triggered when a new message arrives in the Service Bus queue.
    It loads the configuration, figures out where to replicate the message, and then
    calls the replication function to do the actual work.
    """
    logging.info("Service Bus replication function started")
    
    # First, let's load our configuration from environment variables
    try:
        replication_config = ReplicationConfig.from_environment()
        replication_config.validate_destination_config()
    except ValueError as config_error:
        logging.error(f"Configuration problem detected: {config_error}")
        raise ReplicationConfigurationError(str(config_error)) from config_error

    logging.info(
        f"Loaded replication configuration: {replication_config.replication_type}"
    )

    # Figure out where this message should be replicated to
    (dest_connection_string,
     dest_queue_name,
     _) = replication_config.get_destination_config()

    logging.info(f"Replication job starting - {replication_config.direction}")

    # Now do the actual message replication
    replicate_message(
        source_message=msg,
        destination_connection_string=dest_connection_string,
        destination_queue_name=dest_queue_name,
        ttl_seconds=replication_config.ttl_seconds,
        direction=replication_config.direction
    )

    logging.info("Service Bus replication function completed successfully")
