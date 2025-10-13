#!/usr/bin/env python3
"""
Service Bus A to B Replication Script

This script replicates messages from Service Bus A to Service Bus B.
Designed to run in GitHub Actions workflows for automated replication.

Usage:
    python replicate_servicebus_a_to_b.py

Environment Variables:
    SERVICEBUS_A_CONN_STR: Connection string for source Service Bus A
    SERVICEBUS_B_CONN_STR: Connection string for destination Service Bus B
    QUEUE_A_NAME: Queue name in Service Bus A (source)
    QUEUE_B_NAME: Queue name in Service Bus B (destination)
    TOPIC_A_NAME: Topic name in Service Bus A (alternative to queue)
    TOPIC_B_NAME: Topic name in Service Bus B (alternative to queue)
    SUBSCRIPTION_A_NAME: Subscription name for Topic A
    SUBSCRIPTION_B_NAME: Subscription name for Topic B
    BATCH_SIZE: Number of messages to process per batch (default: 10)
    MAX_RETRIES: Maximum retry attempts (default: 3)
    REPLICATION_TIMEOUT: Timeout in seconds (default: 300)
    TTL_RTO_MINUTES: RTO + delta for TTL setting (default: 60)
    USE_TOPICS: Set to 'true' to use topics instead of queues (default: false)
"""

import asyncio
import datetime
import json
import logging
import os
import sys
import time
from typing import Dict, List, Optional

from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus.exceptions import ServiceBusError, ServiceBusConnectionError


class ServiceBusReplicator:
    """Replicates messages from Service Bus A to Service Bus B."""
    
    def __init__(self):
        """Initialize the replicator with environment configuration."""
        self.setup_logging()
        self.load_configuration()
        self.validate_configuration()
        
    def setup_logging(self):
        """Configure logging for GitHub Actions."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_configuration(self):
        """Load configuration from environment variables."""
        self.servicebus_a_conn = os.environ.get('SERVICEBUS_A_CONN_STR')
        self.servicebus_b_conn = os.environ.get('SERVICEBUS_B_CONN_STR')
        
        # Queue/Topic configuration
        self.use_topics = os.environ.get('USE_TOPICS', 'false').lower() == 'true'
        self.queue_a_name = os.environ.get('QUEUE_A_NAME')
        self.queue_b_name = os.environ.get('QUEUE_B_NAME')
        self.topic_a_name = os.environ.get('TOPIC_A_NAME')
        self.topic_b_name = os.environ.get('TOPIC_B_NAME')
        self.subscription_a_name = os.environ.get('SUBSCRIPTION_A_NAME')
        self.subscription_b_name = os.environ.get('SUBSCRIPTION_B_NAME')
        
        # Optional configuration with defaults
        self.batch_size = int(os.environ.get('BATCH_SIZE', '10'))
        self.max_retries = int(os.environ.get('MAX_RETRIES', '3'))
        self.replication_timeout = int(os.environ.get('REPLICATION_TIMEOUT', '300'))
        self.ttl_rto_minutes = int(os.environ.get('TTL_RTO_MINUTES', '60'))
        
        # Filtering configuration
        self.skip_replicated = os.environ.get('SKIP_REPLICATED', 'true').lower() == 'true'
        self.add_metadata = os.environ.get('ADD_METADATA', 'true').lower() == 'true'
        
    def validate_configuration(self):
        """Validate required configuration is present."""
        required_vars = [
            'SERVICEBUS_A_CONN_STR',
            'SERVICEBUS_B_CONN_STR'
        ]
        
        # Check queue vs topic configuration
        if self.use_topics:
            required_vars.extend([
                'TOPIC_A_NAME',
                'TOPIC_B_NAME',
                'SUBSCRIPTION_A_NAME',
                'SUBSCRIPTION_B_NAME'
            ])
            if not all([self.topic_a_name, self.topic_b_name, self.subscription_a_name, self.subscription_b_name]):
                self.logger.error("When USE_TOPICS=true, TOPIC_A_NAME, TOPIC_B_NAME, SUBSCRIPTION_A_NAME, and SUBSCRIPTION_B_NAME are required")
                raise ValueError("Missing topic/subscription configuration")
        else:
            required_vars.extend([
                'QUEUE_A_NAME',
                'QUEUE_B_NAME'
            ])
            if not all([self.queue_a_name, self.queue_b_name]):
                self.logger.error("When USE_TOPICS=false, QUEUE_A_NAME and QUEUE_B_NAME are required")
                raise ValueError("Missing queue configuration")
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            self.logger.error(f"Missing required environment variables: {missing_vars}")
            raise ValueError(f"Missing required environment variables: {missing_vars}")
            
        self.logger.info("Configuration validation passed")
        self.logger.info(f"Replication mode: {'Topics/Subscriptions' if self.use_topics else 'Queues'}")
        self.logger.info(f"TTL RTO setting: {self.ttl_rto_minutes} minutes")
        
    async def test_connections(self):
        """Test connections to both Service Bus instances."""
        self.logger.info("Testing Service Bus connections...")
        
        try:
            # Test Service Bus A connection
            async with ServiceBusClient.from_connection_string(self.servicebus_a_conn) as client:
                try:
                    if self.use_topics:
                        # Test topic and subscription
                        topic_props = await client.get_topic(self.topic_a_name)
                        subscription_props = await client.get_subscription(self.topic_a_name, self.subscription_a_name)
                        self.logger.info(f"✅ Service Bus A connected - Topic: {self.topic_a_name}, Subscription: {self.subscription_a_name} (Active messages: {subscription_props.active_message_count})")
                    else:
                        # Test queue
                        queue_props = await client.get_queue(self.queue_a_name)
                        self.logger.info(f"✅ Service Bus A connected - Queue: {self.queue_a_name} (Active messages: {queue_props.active_message_count})")
                except Exception as e:
                    self.logger.error(f"❌ Service Bus A validation failed: {e}")
                    raise
                    
            # Test Service Bus B connection  
            async with ServiceBusClient.from_connection_string(self.servicebus_b_conn) as client:
                try:
                    if self.use_topics:
                        # Test topic
                        topic_props = await client.get_topic(self.topic_b_name)
                        self.logger.info(f"✅ Service Bus B connected - Topic: {self.topic_b_name}")
                    else:
                        # Test queue
                        queue_props = await client.get_queue(self.queue_b_name)
                        self.logger.info(f"✅ Service Bus B connected - Queue: {self.queue_b_name} (Active messages: {queue_props.active_message_count})")
                except Exception as e:
                    self.logger.error(f"❌ Service Bus B validation failed: {e}")
                    raise
                    
        except ServiceBusConnectionError as e:
            self.logger.error(f"❌ Service Bus connection error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Connection test failed: {e}")
            raise
    
    def should_replicate_message(self, message) -> bool:
        """Determine if a message should be replicated."""
        if not self.skip_replicated:
            return True
            
        # Skip messages that are already replicated to avoid loops
        properties = getattr(message, 'application_properties', {}) or {}
        if properties.get('replicated_from_a_to_b'):
            self.logger.debug(f"Skipping already replicated message: {getattr(message, 'message_id', 'unknown')}")
            return False
            
        return True
    
    def create_replicated_message(self, original_message) -> ServiceBusMessage:
        """Create a new message for replication with metadata and TTL."""
        # Get original message body
        body = original_message.get_body()
        
        # Copy original properties
        properties = {}
        if hasattr(original_message, 'application_properties') and original_message.application_properties:
            properties = dict(original_message.application_properties)
        
        # Add replication metadata if enabled
        if self.add_metadata:
            properties.update({
                'replicated_from_a_to_b': True,
                'replication_timestamp': datetime.datetime.utcnow().isoformat(),
                'original_message_id': getattr(original_message, 'message_id', None),
                'original_enqueued_time': getattr(original_message, 'enqueued_time_utc', datetime.datetime.utcnow()).isoformat(),
                'tier1_replication': True,  # Mark as Tier-1 replication
                'rto_minutes': self.ttl_rto_minutes
            })
        
        # Create new message with TTL (RTO + delta)
        new_message = ServiceBusMessage(body=body, application_properties=properties)
        
        # Set TTL to RTO + delta as per Tier-1 requirements
        ttl_seconds = self.ttl_rto_minutes * 60
        new_message.time_to_live = datetime.timedelta(seconds=ttl_seconds)
        
        # Copy other properties if they exist
        if hasattr(original_message, 'content_type') and original_message.content_type:
            new_message.content_type = original_message.content_type
        if hasattr(original_message, 'correlation_id') and original_message.correlation_id:
            new_message.correlation_id = original_message.correlation_id
        if hasattr(original_message, 'subject') and original_message.subject:
            new_message.subject = original_message.subject
        if hasattr(original_message, 'reply_to') and original_message.reply_to:
            new_message.reply_to = original_message.reply_to
        if hasattr(original_message, 'to') and original_message.to:
            new_message.to = original_message.to
            
        return new_message
    
    async def replicate_messages_batch(self, messages: List, dest_client: ServiceBusClient) -> Dict[str, int]:
        """Replicate a batch of messages to Service Bus B."""
        if not messages:
            return {'processed': 0, 'replicated': 0, 'skipped': 0, 'failed': 0}
        
        # Filter messages that should be replicated
        messages_to_replicate = [msg for msg in messages if self.should_replicate_message(msg)]
        skipped_count = len(messages) - len(messages_to_replicate)
        
        if not messages_to_replicate:
            self.logger.info(f"Skipped {skipped_count} messages (already replicated or filtered)")
            return {'processed': len(messages), 'replicated': 0, 'skipped': skipped_count, 'failed': 0}
        
        # Transform messages for replication
        replicated_messages = [self.create_replicated_message(msg) for msg in messages_to_replicate]
        
        # Send to Service Bus B with retry logic
        for attempt in range(1, self.max_retries + 1):
            try:
                if self.use_topics:
                    # Send to topic
                    async with dest_client.get_topic_sender(topic_name=self.topic_b_name) as sender:
                        await sender.send_messages(replicated_messages)
                        self.logger.info(f"Successfully sent {len(replicated_messages)} messages to Service Bus B topic: {self.topic_b_name}")
                else:
                    # Send to queue
                    async with dest_client.get_queue_sender(queue_name=self.queue_b_name) as sender:
                        await sender.send_messages(replicated_messages)
                        self.logger.info(f"Successfully sent {len(replicated_messages)} messages to Service Bus B queue: {self.queue_b_name}")
                    
                self.logger.info(f"Successfully replicated {len(replicated_messages)} messages to Service Bus B (attempt {attempt})")
                self.logger.info(f"TTL set to {self.ttl_rto_minutes} minutes (RTO+delta) for Tier-1 compliance")
                return {
                    'processed': len(messages),
                    'replicated': len(replicated_messages), 
                    'skipped': skipped_count,
                    'failed': 0
                }
                
            except ServiceBusError as e:
                self.logger.warning(f"Replication attempt {attempt} failed: {e}")
                if attempt == self.max_retries:
                    self.logger.error(f"Failed to replicate {len(replicated_messages)} messages after {self.max_retries} attempts")
                    return {
                        'processed': len(messages),
                        'replicated': 0,
                        'skipped': skipped_count, 
                        'failed': len(replicated_messages)
                    }
                else:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    self.logger.info(f"Waiting {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)
        
        return {'processed': len(messages), 'replicated': 0, 'skipped': skipped_count, 'failed': len(replicated_messages)}
    
    async def run_replication_cycle(self) -> Dict[str, int]:
        """Run a single replication cycle."""
        self.logger.info("Starting replication cycle from Service Bus A to Service Bus B")
        
        total_stats = {'processed': 0, 'replicated': 0, 'skipped': 0, 'failed': 0}
        
        try:
            # Connect to both Service Bus instances
            async with ServiceBusClient.from_connection_string(self.servicebus_a_conn) as source_client:
                async with ServiceBusClient.from_connection_string(self.servicebus_b_conn) as dest_client:
                    
                    # Get receiver from Service Bus A (Queue or Topic Subscription)
                    if self.use_topics:
                        async with source_client.get_subscription_receiver(
                            topic_name=self.topic_a_name, 
                            subscription_name=self.subscription_a_name
                        ) as receiver:
                            await self._process_messages_from_receiver(receiver, dest_client, total_stats)
                    else:
                        async with source_client.get_queue_receiver(queue_name=self.queue_a_name) as receiver:
                            await self._process_messages_from_receiver(receiver, dest_client, total_stats)
                            
        except ServiceBusConnectionError as e:
            self.logger.error(f"Service Bus connection error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during replication: {e}")
            raise
        
        return total_stats
    
    async def _process_messages_from_receiver(self, receiver, dest_client, total_stats):
        """Process messages from a receiver (queue or subscription)."""
        while True:
            messages = await receiver.receive_messages(
                max_message_count=self.batch_size,
                max_wait_time=10  # Wait 10 seconds for messages
            )
            
            if not messages:
                source_name = f"{self.topic_a_name}/{self.subscription_a_name}" if self.use_topics else self.queue_a_name
                self.logger.info(f"No more messages available in Service Bus A ({source_name})")
                break
            
            source_name = f"{self.topic_a_name}/{self.subscription_a_name}" if self.use_topics else self.queue_a_name
            self.logger.info(f"📤 Received {len(messages)} messages from Service Bus A ({source_name})")
            
            # Replicate the batch
            batch_stats = await self.replicate_messages_batch(messages, dest_client)
            
            # Update total statistics
            for key in total_stats:
                total_stats[key] += batch_stats[key]
            
            # Complete successfully processed messages
            messages_to_complete = []
            if batch_stats['replicated'] > 0 or batch_stats['skipped'] > 0:
                # Complete all messages that were either replicated or skipped
                messages_to_complete = messages
            else:
                # If replication failed, only complete skipped messages
                messages_to_complete = [msg for msg in messages if not self.should_replicate_message(msg)]
            
            if messages_to_complete:
                await receiver.complete_messages(messages_to_complete)
                self.logger.info(f"Completed {len(messages_to_complete)} messages in Service Bus A")
            
            # Log batch results
            self.logger.info(
                f"Batch complete - Processed: {batch_stats['processed']}, "
                f"Replicated: {batch_stats['replicated']}, "
                f"Skipped: {batch_stats['skipped']}, "
                f"Failed: {batch_stats['failed']}"
            )
    
    async def run_timed_replication(self) -> Dict[str, int]:
        """Run replication for a specified timeout period."""
        self.logger.info(f"Starting timed replication (timeout: {self.replication_timeout} seconds)")
        
        start_time = time.time()
        total_stats = {'processed': 0, 'replicated': 0, 'skipped': 0, 'failed': 0}
        
        while (time.time() - start_time) < self.replication_timeout:
            try:
                cycle_stats = await self.run_replication_cycle()
                
                # Update total statistics
                for key in total_stats:
                    total_stats[key] += cycle_stats[key]
                
                # If no messages were processed, wait before next cycle
                if cycle_stats['processed'] == 0:
                    self.logger.info("No messages processed, waiting 30 seconds before next cycle...")
                    await asyncio.sleep(30)
                else:
                    # Short pause between cycles when messages are active
                    await asyncio.sleep(5)
                    
            except Exception as e:
                self.logger.error(f"Error in replication cycle: {e}")
                await asyncio.sleep(10)  # Wait before retrying
        
        elapsed_time = time.time() - start_time
        self.logger.info(f"Timed replication completed after {elapsed_time:.1f} seconds")
        
        return total_stats
    
    def log_summary(self, stats: Dict[str, int]):
        """Log final replication summary."""
        self.logger.info("=" * 60)
        self.logger.info("REPLICATION SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total messages processed: {stats['processed']}")
        self.logger.info(f"Messages replicated to Service Bus B: {stats['replicated']}")
        self.logger.info(f"Messages skipped (already replicated): {stats['skipped']}")
        self.logger.info(f"Messages failed to replicate: {stats['failed']}")
        
        success_rate = (stats['replicated'] / stats['processed'] * 100) if stats['processed'] > 0 else 0
        self.logger.info(f"Success rate: {success_rate:.1f}%")
        
        if stats['failed'] > 0:
            self.logger.warning(f"⚠️ {stats['failed']} messages failed to replicate")
        
        if stats['replicated'] > 0:
            self.logger.info(f"✅ Successfully replicated {stats['replicated']} messages")
        
        # Set GitHub Actions output for use in workflow
        if os.environ.get('GITHUB_ACTIONS'):
            github_output = os.environ.get('GITHUB_OUTPUT')
            if github_output:
                with open(github_output, 'a') as f:
                    f.write(f"messages_processed={stats['processed']}\n")
                    f.write(f"messages_replicated={stats['replicated']}\n")
                    f.write(f"messages_failed={stats['failed']}\n")
                    f.write(f"success_rate={success_rate:.1f}\n")


async def main():
    """Main entry point for the replication script."""
    try:
        # Create and run replicator
        replicator = ServiceBusReplicator()
        
        # Test connections first
        await replicator.test_connections()
        
        # Log configuration (without sensitive data)
        replicator.logger.info("Service Bus A to B Replication Started")
        replicator.logger.info("=" * 50)
        replicator.logger.info("🔄 Tier-1 Service Bus Replication for Cross-Region Resiliency")
        
        if replicator.use_topics:
            replicator.logger.info(f"Source: Topic '{replicator.topic_a_name}' / Subscription '{replicator.subscription_a_name}'")
            replicator.logger.info(f"Destination: Topic '{replicator.topic_b_name}'")
        else:
            replicator.logger.info(f"Source Queue: {replicator.queue_a_name}")
            replicator.logger.info(f"Destination Queue: {replicator.queue_b_name}")
            
        replicator.logger.info(f"Batch Size: {replicator.batch_size}")
        replicator.logger.info(f"Max Retries: {replicator.max_retries}")
        replicator.logger.info(f"Timeout: {replicator.replication_timeout} seconds")
        replicator.logger.info(f"TTL (RTO+delta): {replicator.ttl_rto_minutes} minutes")
        replicator.logger.info("=" * 50)
        
        # Run replication
        stats = await replicator.run_timed_replication()
        
        # Log summary
        replicator.log_summary(stats)
        
        # Exit with appropriate code
        if stats['failed'] > 0:
            replicator.logger.error("🚨 Replication completed with failures")
            sys.exit(1)
        else:
            replicator.logger.info("🎉 Service Bus replication completed successfully!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logging.info("Replication interrupted by user")
        sys.exit(130)
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
