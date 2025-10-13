Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-13T20:35:05.848Z] Replication cron failed: Unexpected error during message replication: 'ServiceBusReceivedMessage' object has no attribute 'get_body'
Traceback (most recent call last):
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\main.py", line 111, in _handle_replication_exceptions
    send_fn(correlation_id=correlation_id)
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\retry_utils.py", line 48, in wrapper
    return func(*args, **kwargs)
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\main.py", line 76, in send_with_retry
    replicated = create_replicated_message(
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\message_utils.py", line 138, in create_replicated_message
    source_body = source_message.get_body()
AttributeError: 'ServiceBusReceivedMessage' object has no attribute 'get_body'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\main.py", line 184, in main     
    orchestrate_replication(msg, config)
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\main.py", line 149, in orchestrate_replication
    replicate_message_to_destination(source_message, dest_conn, dest_topic,
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\main.py", line 142, in replicate_message_to_destination
    _handle_replication_exceptions(send_fn, corr_id, direction, dest_topic, app_logger)
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\main.py", line 125, in _handle_replication_exceptions
    handle_unexpected_error(e, correlation_id, direction, dest_topic, logger)
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\error_handlers.py", line 168, in handle_unexpected_error
    raise ReplicationError(
__app__.src.exceptions.ReplicationError: Unexpected error during message replication: 'ServiceBusReceivedMessage' object has no attribute 'get_body'
[2025-10-13T20:35:06.125Z] Executed 'Functions.src' (Succeeded, Id=9b0005c4-0f15-430b-ac5b-984ef5a0ed1a, Duration=6099ms)