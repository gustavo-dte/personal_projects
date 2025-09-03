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
    
    # Dead letter queue configuration for failed replication attempts
    dead_letter_enabled: bool = True
    max_delivery_count: int = 3  # Max attempts before sending to dead letter queue
    dlq_time_to_live_minutes: int = 1440  # 24 hours in dead letter queue

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
                "This setting is required to determine replication direction. "
                "Valid values: 'primary_to_secondary' or 'secondary_to_primary'"
            )
        
        replication_type = replication_type_raw.lower()
        allowed_types = ["primary_to_secondary", "secondary_to_primary"]
        if replication_type not in allowed_types:
            raise ValueError(
                f"Invalid REPLICATION_TYPE: '{replication_type_raw}'. "
                f"Must be one of: {', '.join(allowed_types)}"
            )

        # Get the connection strings and queue names
        # We'll validate these based on the replication direction
        primary_connection_string = os.environ.get("PRIMARY_SERVICEBUS_CONN")
        primary_queue_name = os.environ.get("PRIMARY_QUEUE_NAME")
        secondary_connection_string = os.environ.get("SECONDARY_SERVICEBUS_CONN")
        secondary_queue_name = os.environ.get("SECONDARY_QUEUE_NAME")

        # Validate required environment variables based on replication type
        missing_vars = []
        if replication_type == "primary_to_secondary":
            if not secondary_connection_string:
                missing_vars.append("SECONDARY_SERVICEBUS_CONN")
            if not secondary_queue_name:
                missing_vars.append("SECONDARY_QUEUE_NAME")
        elif replication_type == "secondary_to_primary":
            if not primary_connection_string:
                missing_vars.append("PRIMARY_SERVICEBUS_CONN")
            if not primary_queue_name:
                missing_vars.append("PRIMARY_QUEUE_NAME")
                
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables for {replication_type}: "
                f"{', '.join(missing_vars)}. These are required for the "
                f"destination configuration."
            )

        # Get the timing settings with sensible defaults and validate them
        try:
            rto_minutes_str = os.environ.get("RTO_MINUTES", "10")
            delta_minutes_str = os.environ.get("DELTA_MINUTES", "2")
            
            recovery_time_minutes = int(rto_minutes_str)
            buffer_minutes = int(delta_minutes_str)
            
            # Validate reasonable ranges
            if recovery_time_minutes <= 0:
                raise ValueError("RTO_MINUTES must be a positive integer")
            if buffer_minutes < 0:
                raise ValueError("DELTA_MINUTES must be a non-negative integer")
                
        except ValueError as conversion_error:
            raise ValueError(
                f"Invalid timing configuration: {conversion_error}. "
                "RTO_MINUTES and DELTA_MINUTES must be valid positive integers."
            ) from conversion_error

        # Handle dead letter queue configuration from environment variables
        try:
            dlq_enabled_str = os.environ.get("DLQ_ENABLED", "true")
            max_delivery_str = os.environ.get("MAX_DELIVERY_COUNT", "3")
            dlq_ttl_minutes_str = os.environ.get("DLQ_TTL_MINUTES", "1440")
            
            dlq_enabled = dlq_enabled_str.lower() == "true"
            max_delivery = int(max_delivery_str)
            dlq_ttl_minutes = int(dlq_ttl_minutes_str)
            
            # Validate reasonable ranges
            if max_delivery <= 0:
                raise ValueError("MAX_DELIVERY_COUNT must be a positive integer")
            if dlq_ttl_minutes <= 0:
                raise ValueError("DLQ_TTL_MINUTES must be a positive integer")
                
        except ValueError as dlq_error:
            raise ValueError(
                f"Invalid dead letter queue configuration: {dlq_error}. "
                "MAX_DELIVERY_COUNT and DLQ_TTL_MINUTES must be valid positive "
                "integers, and DLQ_ENABLED must be 'true' or 'false'."
            ) from dlq_error

        return cls(
            replication_type=replication_type,
            primary_conn_str=primary_connection_string,
            primary_queue=primary_queue_name,
            secondary_conn_str=secondary_connection_string,
            secondary_queue=secondary_queue_name,
            rto_minutes=recovery_time_minutes,
            delta_minutes=buffer_minutes,
            dead_letter_enabled=dlq_enabled,
            max_delivery_count=max_delivery,
            dlq_time_to_live_minutes=dlq_ttl_minutes,
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
