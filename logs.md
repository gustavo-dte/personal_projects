[2025-10-13T20:46:04.918Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-13T20:46:04.918Z] Management link receiver state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-13T20:46:05.261Z] AMQP error occurred: (TokenAuthFailure('CBS Token authentication failed.\nStatus code: None')), condition: (<ErrorCondition.ClientError: b'amqp:client-error'>), description: (None).
[2025-10-13T20:46:05.265Z] AMQP Connection authentication error occurred: (TokenAuthFailure('CBS Token authentication failed.\nStatus code: None')).
[2025-10-13T20:46:05.266Z] 'servicebus.pysdk-d5645b42' operation has exhausted retry. Last exception: ServiceBusAuthenticationError('Service Bus has encountered an error. Error condition: amqp:client-error.').
[2025-10-13T20:46:05.267Z] All 3 retry attempts failed
[2025-10-13T20:46:05.268Z] Service Bus replication error: unexpected_error
[2025-10-13T20:46:05.268Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-13T20:46:05.270Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-13T20:46:05.270Z] Management link receiver state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-13T20:46:05.282Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-13T20:46:05.412Z] Management link sender state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-13T20:46:05.412Z] Session state changed: <SessionState.MAPPED: 3> -> <SessionState.END_SENT: 4>
[2025-10-13T20:46:05.413Z] Connection state changed: <ConnectionState.OPENED: 9> -> <ConnectionState.CLOSE_SENT: 11>
[2025-10-13T20:46:05.415Z] Connection state changed: <ConnectionState.CLOSE_SENT: 11> -> <ConnectionState.END: 13>  
[2025-10-13T20:46:05.442Z] Session state changed: <SessionState.END_SENT: 4> -> <SessionState.DISCARDING: 6>
[2025-10-13T20:46:05.442Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-13T20:46:05.443Z] Management link sender state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-13T20:46:05.444Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-13T20:46:05.444Z] Management link receiver state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-13T20:46:05.445Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-13T20:46:05.684Z] Replication cron failed: Unexpected error during message replication: All 3 retry attempts failed: Service Bus has encountered an error. Error condition: amqp:client-error.
Traceback (most recent call last):
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\retry_utils.py", line 48, in wrapper
    return func(*args, **kwargs)
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\main.py", line 81, in send_with_retry
    send_message_to_destination(dest_conn, dest_topic, replicated, correlation_id)
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\main.py", line 65, in send_message_to_destination
    with client.get_topic_sender(topic_name=dest_topic) as sender:
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\.venv\Lib\site-packages\azure\servicebus\_servicebus_sender.py", line 202, in __enter__
    self._open_with_retry()
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\.venv\Lib\site-packages\azure\servicebus\_base_handler.py", line 545, in _open_with_retry
    return self._do_retryable_operation(self._open)
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\.venv\Lib\site-packages\azure\servicebus\_base_handler.py", line 413, in _do_retryable_operation
    raise last_exception from None
azure.servicebus.exceptions.ServiceBusAuthenticationError: Service Bus has encountered an error. Error condition: amqp:client-error.

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\main.py", line 111, in _handle_replication_exceptions
    send_fn(correlation_id=correlation_id)
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\retry_utils.py", line 70, in wrapper
    raise ReplicationError(
__app__.src.exceptions.ReplicationError: All 3 retry attempts failed: Service Bus has encountered an error. Error condition: amqp:client-error.

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
__app__.src.exceptions.ReplicationError: Unexpected error during message replication: All 3 retry attempts failed: Service Bus has encountered an error. Error condition: amqp:client-error.
[2025-10-13T20:46:05.983Z] Executed 'Functions.src' (Succeeded, Id=8ba54470-3b30-4ec8-b2ad-afbec83a1d75, Duration=65943ms)