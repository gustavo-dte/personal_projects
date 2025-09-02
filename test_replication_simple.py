#!/usr/bin/env python3
"""
Test Service Bus A to B Replication

This script tests the replication functionality by sending test messages
and verifying they are properly replicated.
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime

from azure.servicebus import ServiceBusClient, ServiceBusMessage


async def test_connections(servicebus_a_conn: str, servicebus_b_conn: str, queue_a_name: str, queue_b_name: str):
    """Test connections to both Service Bus instances."""
    print("🔌 Testing Service Bus connections...")
    
    try:
        # Test Service Bus A
        async with ServiceBusClient.from_connection_string(servicebus_a_conn) as client:
            queue_props = await client.get_queue(queue_a_name)
            print(f"✅ Service Bus A connected - Queue: {queue_a_name} (Active messages: {queue_props.active_message_count})")
            
        # Test Service Bus B
        async with ServiceBusClient.from_connection_string(servicebus_b_conn) as client:
            queue_props = await client.get_queue(queue_b_name)
            print(f"✅ Service Bus B connected - Queue: {queue_b_name} (Active messages: {queue_props.active_message_count})")
            
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


async def send_test_messages_to_a(conn_str: str, queue_name: str, count: int = 3):
    """Send test messages to Service Bus A."""
    print(f"📤 Sending {count} test messages to Service Bus A...")
    
    async with ServiceBusClient.from_connection_string(conn_str) as client:
        async with client.get_queue_sender(queue_name=queue_name) as sender:
            
            messages = []
            for i in range(count):
                test_data = {
                    'test_id': str(uuid.uuid4()),
                    'message_number': i + 1,
                    'timestamp': datetime.utcnow().isoformat(),
                    'test_type': 'replication_test',
                    'content': f'Test message {i + 1} for replication validation'
                }
                
                message = ServiceBusMessage(
                    body=json.dumps(test_data).encode('utf-8'),
                    application_properties={
                        'messageType': 'test',
                        'testRun': datetime.utcnow().isoformat(),
                        'messageNumber': str(i + 1)
                    }
                )
                messages.append(message)
            
            await sender.send_messages(messages)
            print(f"✅ Successfully sent {count} test messages to Service Bus A")
            
            # Return test IDs for verification
            return [json.loads(msg.get_body().decode('utf-8'))['test_id'] for msg in messages]


async def check_messages_in_b(conn_str: str, queue_name: str, test_ids: list, timeout: int = 60):
    """Check if test messages were replicated to Service Bus B."""
    print(f"📥 Checking for replicated messages in Service Bus B (timeout: {timeout}s)...")
    
    found_messages = []
    start_time = asyncio.get_event_loop().time()
    
    async with ServiceBusClient.from_connection_string(conn_str) as client:
        async with client.get_queue_receiver(queue_name=queue_name) as receiver:
            
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                messages = await receiver.receive_messages(max_message_count=10, max_wait_time=5)
                
                if not messages:
                    print("⏳ Waiting for replicated messages...")
                    await asyncio.sleep(5)
                    continue
                
                for message in messages:
                    try:
                        body = json.loads(message.get_body().decode('utf-8'))
                        properties = getattr(message, 'application_properties', {}) or {}
                        
                        # Check if this is one of our test messages
                        if body.get('test_id') in test_ids:
                            found_messages.append({
                                'test_id': body.get('test_id'),
                                'message_number': body.get('message_number'),
                                'replicated': properties.get('replicated_from_a_to_b', False),
                                'replication_timestamp': properties.get('replication_timestamp'),
                                'original_timestamp': body.get('timestamp')
                            })
                            print(f"✅ Found replicated message: {body.get('test_id')}")
                        
                        # Complete all messages (test and non-test)
                        await receiver.complete_message(message)
                        
                    except Exception as e:
                        print(f"⚠️ Error processing message: {e}")
                        await receiver.complete_message(message)
                
                # If we found all our test messages, we can stop
                if len(found_messages) >= len(test_ids):
                    break
    
    return found_messages


async def run_replication_test():
    """Run the complete replication test."""
    print("🧪 Service Bus A to B Replication Test")
    print("=" * 50)
    
    # Get configuration
    servicebus_a_conn = os.environ.get('SERVICEBUS_A_CONN_STR')
    servicebus_b_conn = os.environ.get('SERVICEBUS_B_CONN_STR')
    queue_a_name = os.environ.get('QUEUE_A_NAME')
    queue_b_name = os.environ.get('QUEUE_B_NAME')
    
    if not all([servicebus_a_conn, servicebus_b_conn, queue_a_name, queue_b_name]):
        print("❌ Missing required environment variables")
        print("Required: SERVICEBUS_A_CONN_STR, SERVICEBUS_B_CONN_STR, QUEUE_A_NAME, QUEUE_B_NAME")
        return False
    
    # Test connections first
    if not await test_connections(servicebus_a_conn, servicebus_b_conn, queue_a_name, queue_b_name):
        print("❌ Connection test failed. Please check your configuration.")
        return False
    
    try:
        # Step 1: Send test messages to Service Bus A
        print(f"\n📤 Step 1: Sending test messages to Service Bus A")
        test_ids = await send_test_messages_to_a(servicebus_a_conn, queue_a_name, 3)
        print(f"Test message IDs: {test_ids}")
        
        print(f"\n⏳ Step 2: Waiting 30 seconds for replication to occur...")
        await asyncio.sleep(30)
        
        # Step 2: Check if messages were replicated to Service Bus B
        print(f"\n📥 Step 3: Checking for replicated messages in Service Bus B")
        found_messages = await check_messages_in_b(servicebus_b_conn, queue_b_name, test_ids, 60)
        
        # Step 3: Analyze results
        print(f"\n📊 Step 4: Test Results Analysis")
        print("=" * 40)
        print(f"Messages sent to Service Bus A: {len(test_ids)}")
        print(f"Messages found in Service Bus B: {len(found_messages)}")
        
        if len(found_messages) == len(test_ids):
            print("🎉 SUCCESS: All test messages were successfully replicated!")
            
            # Check replication metadata
            replicated_count = sum(1 for msg in found_messages if msg['replicated'])
            print(f"Messages with replication metadata: {replicated_count}")
            
            for msg in found_messages:
                status = '✅ Replicated' if msg['replicated'] else '⚠️ No metadata'
                print(f"  - Message {msg['message_number']}: {status}")
                if msg['replication_timestamp']:
                    print(f"    Replicated at: {msg['replication_timestamp']}")
            
            return True
            
        else:
            print(f"❌ PARTIAL SUCCESS: Only {len(found_messages)}/{len(test_ids)} messages were replicated")
            
            missing_ids = set(test_ids) - {msg['test_id'] for msg in found_messages}
            if missing_ids:
                print(f"Missing messages: {list(missing_ids)}")
            
            return False
    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


async def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Service Bus A to B Replication Test")
        print("")
        print("This script tests the replication by:")
        print("1. Sending test messages to Service Bus A")
        print("2. Waiting for replication to occur")
        print("3. Checking if messages appear in Service Bus B")
        print("")
        print("Required environment variables:")
        print("- SERVICEBUS_A_CONN_STR: Connection string for Service Bus A")
        print("- SERVICEBUS_B_CONN_STR: Connection string for Service Bus B")
        print("- QUEUE_A_NAME: Queue name in Service Bus A")
        print("- QUEUE_B_NAME: Queue name in Service Bus B")
        return
    
    success = await run_replication_test()
    
    if success:
        print("\n✅ Replication test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Replication test failed!")
        print("\nTroubleshooting tips:")
        print("1. Ensure the replication script is running")
        print("2. Check Service Bus connection strings and permissions")
        print("3. Verify queue names are correct")
        print("4. Check for any errors in the replication logs")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
