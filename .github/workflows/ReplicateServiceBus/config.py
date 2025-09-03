"""
Configuration handling for the Service Bus replication function.

This module contains the configuration dataclass that handles all the environment
variables and settings needed for replicating messages between Service Bus instances.
"""

import os
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ReplicationConfig:
    """
    Holds all the configuration needed for Service Bus message replication.

    This is an immutable dataclass (frozen=True) that contains all the settings
    we need to replicate messages between primary and secondary Service Bus instances.
    Using an immutable class helps prevent accidental modifications and makes the
    configuration more predictable.
    """

    replication_type: Literal["primary_to_secondary", "secondary_to_primary"]
    primary_conn_str: str | None
    primary_queue: str | None
    secondary_conn_str: str | None
    secondary_queue: str | None
    rto_minutes: int  # Recovery Time Objective in minutes
    delta_minutes: int  # Additional buffer time in minutes

    @classmethod
    def from_environment(cls) -> "ReplicationConfig":
        """
        Creates a configuration instance by reading environment variables.
        
        This is the main way to create a ReplicationConfig instance. It reads all
        the necessary environment variables and validates them before creating
        the configuration object.
        
        Returns:
            ReplicationConfig: A new configuration instance with all settings loaded
            
        Raises:
            ValueError: If any required environment variables are missing or have
                       invalid values
        """
        # First, let's get the replication type and make sure it's valid
        replication_type_raw = os.environ.get("REPLICATION_TYPE")
        if not replication_type_raw:
            raise ValueError(
                "REPLICATION_TYPE environment variable is not set. "
                "This setting is required to determine replication direction."
            )
        
        replication_type = replication_type_raw.lower()
        allowed_types = ["primary_to_secondary", "secondary_to_primary"]
        if replication_type not in allowed_types:
            raise ValueError(
                "Invalid REPLICATION_TYPE: {}. Must be one of: {}".format(
                    replication_type, ', '.join(allowed_types)
                )
            )

        # Now get the connection strings and queue names
        # These might be None if not set, which we'll validate later
        primary_connection_string = os.environ.get("PRIMARY_SERVICEBUS_CONN")
        primary_queue_name = os.environ.get("PRIMARY_QUEUE_NAME")
        secondary_connection_string = os.environ.get("SECONDARY_SERVICEBUS_CONN")
        secondary_queue_name = os.environ.get("SECONDARY_QUEUE_NAME")

        # Get the timing settings with sensible defaults
        try:
            recovery_time_minutes = int(os.environ.get("RTO_MINUTES", "10"))
            buffer_minutes = int(os.environ.get("DELTA_MINUTES", "2"))
        except ValueError as conversion_error:
            raise ValueError(
                "RTO_MINUTES and DELTA_MINUTES must be valid integer values"
            ) from conversion_error

        return cls(
            replication_type=replication_type,
            primary_conn_str=primary_connection_string,
            primary_queue=primary_queue_name,
            secondary_conn_str=secondary_connection_string,
            secondary_queue=secondary_queue_name,
            rto_minutes=recovery_time_minutes,
            delta_minutes=buffer_minutes,
        )

    @property
    def ttl_seconds(self) -> int:
        """
        Calculates the Time To Live for replicated messages in seconds.
        
        We add the RTO (Recovery Time Objective) and delta time together to give
        messages enough time to be processed before they expire.

        Returns:
            int: Total TTL in seconds
        """
        total_minutes = self.rto_minutes + self.delta_minutes
        return total_minutes * 60

    @property
    def direction(self) -> str:
        """
        Returns a human-friendly description of the replication direction.
        
        This is mainly used for logging to make it clear which direction
        the replication is happening.

        Returns:
            str: A readable description like "Primary → Secondary"
        """
        if self.replication_type == "primary_to_secondary":
            return "Primary → Secondary"
        else:  # Must be secondary_to_primary due to validation
            return "Secondary → Primary"

    def get_destination_config(self) -> tuple[str | None, str | None, str]:
        """
        Figures out the destination connection info based on replication type.
        
        This method looks at the replication direction and returns the appropriate
        destination connection string and queue name.

        Returns:
            tuple: (connection_string, queue_name, direction_description)
        """
        if self.replication_type == "primary_to_secondary":
            # We're replicating from primary to secondary
            return (
                self.secondary_conn_str,
                self.secondary_queue,
                self.direction
            )
        else:  # secondary_to_primary
            # We're replicating from secondary to primary
            return (
                self.primary_conn_str,
                self.primary_queue,
                self.direction
            )

    def validate_destination_config(self) -> None:
        """
        Makes sure we have all the connection info we need for the destination.
        
        This validation method checks that the required connection string and
        queue name are available for whichever direction we're replicating to.

        Raises:
            ValueError: If any required connection information is missing
        """
        destination_conn_str, destination_queue, _ = self.get_destination_config()

        # Check if we have a connection string for the destination
        if not destination_conn_str:
            if self.replication_type == "primary_to_secondary":
                missing_variable = "SECONDARY_SERVICEBUS_CONN"
            else:
                missing_variable = "PRIMARY_SERVICEBUS_CONN"
            raise ValueError(
                f"Missing required environment variable: {missing_variable}"
            )

        # Check if we have a queue name for the destination
        if not destination_queue:
            if self.replication_type == "primary_to_secondary":
                missing_variable = "SECONDARY_QUEUE_NAME"
            else:
                missing_variable = "PRIMARY_QUEUE_NAME"
            raise ValueError(
                f"Missing required environment variable: {missing_variable}"
            )
