eceiver: AbandonAsync start. MessageCount = 1, LockToken = 9af119cc-15b5-413e-8d68-c0d5987f00cb
[2025-10-02T00:26:36.147Z] Invocation cancelled - exiting retry loop.
[2025-10-02T00:26:36.154Z] dte-notifications/Subscriptions/email-notifications-b0789281-a614-4483-9a35-6386983a0ab0: User message handler complete: Message: SequenceNumber: 57139420272263169, Exception: Microsoft.Azure.WebJobs.Host.FunctionInvocationException: Exception while executing function: Functions.replication_fuction
[2025-10-02T00:26:36.541Z]  ---> Microsoft.Azure.WebJobs.Script.Workers.Rpc.RpcException: Result: Failure
Exception: TypeError: orchestrate_replication() got an unexpected keyword argument 'logger'
Stack:   File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\dispatcher.py", line 676, in _handle__invocation_request
    call_result = await self._loop.run_in_executor(
  File "C:\Python\Lib\concurrent\futures\thread.py", line 58, in run
    result = self.fn(*self.args, **self.kwargs)
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\dispatcher.py", line 1006, in _run_sync_func
    return ExtensionManager.get_sync_invocation_wrapper(context,
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\extension.py", line 211, in _raw_invocation_wrapper
    result = function(**args)
  File "C:\Users\u69819\Documents\DevOps\service_bus\cloud-platform-servicebus-replication\src\replication_fuction\__init__.py", line 27, in main
    orchestrate_replication(source_message=msg, replication_config=config, logger=logger)

[2025-10-02T00:26:36.703Z]    at Microsoft.Azure.WebJobs.Script.Description.WorkerFunctionInvoker.InvokeCore(Object[] parameters, FunctionInvocationContext context) in /_/src/WebJobs.Script/Description/Workers/WorkerFunctionInvoker.cs:line 101
[2025-10-02T00:26:36.704Z]    at Microsoft.Azure.WebJobs.Script.Description.FunctionInvokerBase.Invoke(Object[] parameters) in /_/src/WebJobs.Script/Description/FunctionInvokerBase.cs:line 82
[2025-10-02T00:26:36.710Z]    at Microsoft.Azure.WebJobs.Host.Executors.VoidTaskMethodInvoker`2.InvokeAsync(TReflected instance, Object[] arguments) in D:\a\_work\1\s\src\Microsoft.Azure.WebJobs.Host\Executors\VoidTaskMethodInvoker.cs:line 20
[2025-10-02T00:26:36.711Z]    at Microsoft.Azure.WebJobs.Host.Executors.FunctionInvoker`2.InvokeAsync(Object instance, Object[] arguments) in D:\a\_work\1\s\src\Microsoft.Azure.WebJobs.Host\Executors\FunctionInvoker.cs:line 53        
[2025-10-02T00:26:36.711Z]    at Microsoft.Azure.WebJobs.Host.Executors.FunctionExecutor.InvokeWithTimeoutAsync(IFunctionInvoker invoker, ParameterHelper parameterHelper, CancellationTokenSource timeoutTokenSource, CancellationTokenSource functionCancellationTokenSource, Boolean throwOnTimeout, TimeSpan timerInterval, IFunctionInstance instance) in D:\a\_work\1\s\src\Microsoft.Azure.WebJobs.Host\Executors\FunctionExecutor.cs:line 581
[2025-10-02T00:26:36.718Z]    at Microsoft.Azure.WebJobs.Host.Executors.FunctionExecutor.ExecuteWithWatchersAsync(IFunctionInstanceEx instance, ParameterHelper parameterHelper, ILogger logger, CancellationTokenSource functionCancellationTokenSource) in D:\a\_work\1\s\src\Microsoft.Azure.WebJobs.Host\Executors\FunctionExecutor.cs:line 527
[2025-10-02T00:26:36.719Z]    at Microsoft.Azure.WebJobs.Host.Executors.FunctionExecutor.ExecuteWithLoggingAsync(IFunctionInstanceEx instance, FunctionStartedMessage message, FunctionInstanceLogEntry instanceLogEntry, ParameterHelper parameterHelper, ILogger logger, CancellationToken cancellationToken) in D:\a\_work\1\s\src\Microsoft.Azure.WebJobs.Host\Executors\FunctionExecutor.cs:line 306
[2025-10-02T00:26:36.720Z]    --- End of inner exception stack trace ---
[2025-10-02T00:26:36.720Z]    at Microsoft.Azure.WebJobs.ServiceBus.MessageProcessor.CompleteProcessingMessageAsync(ServiceBusMessageActions actions, ServiceBusReceivedMessage message, FunctionResult result, CancellationToken cancellationToken)
[2025-10-02T00:26:36.721Z]    at Microsoft.Azure.WebJobs.ServiceBus.Listeners.ServiceBusListener.ProcessMessageAsync(ProcessMessageEventArgs args)
[2025-10-02T00:26:36.721Z]    at Azure.Messaging.ServiceBus.ServiceBusProcessor.OnProcessMessageAsync(ProcessMessageEventArgs args)
[2025-10-02T00:26:36.722Z]    at Azure.Messaging.ServiceBus.ReceiverManager.OnMessageHandler(EventArgs args)
[2025-10-02T00:26:36.722Z]    at Azure.Messaging.ServiceBus.ReceiverManager.ProcessOneMessage(ServiceBusReceivedMessage triggerMessage, CancellationToken cancellationToken), LockToken: 0a1b6955-a995-483b-b7cd-d3cd406100cb
[2025-10-02T00:26:36.723Z] Message processing error (Action=ProcessMessageCallback, EntityPath=dte-notifications/Subscriptions/email-notifications, Endpoint=sbns-cu-dev-sos.servicebus.windows.net)
[2025-10-02T00:26:36.941Z] System.Private.CoreLib: Exception while executing function: Functions.replication_fuction. System.Private.CoreLib: Result: Failure
Exception: TypeError: orchestrate_replication() got an unexpected keyword argument 'logger'
Stack:   File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\dispatcher.py", line 676, in _handle__invocation_request
    call_result = await self._loop.run_in_executor(
  File "C:\Python\Lib\concurrent\futures\thread.py", line 58, in run
    result = self.fn(*self.args, **self.kwargs)
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\dispatcher.py", line 1006, in _run_sync_func
    return ExtensionManager.get_sync_invocation_wrapper(context,
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\extension.py", line 211, in _raw_invocation_wrapper
    result = function(**args)
  File "C:\Users\u69819\Documents\DevOps\service_bus\cloud-platform-servicebus-replication\src\replication_fuction\__init__.py", line 27, in main
    orchestrate_replication(source_message=msg, replication_config=config, logger=logger)