[2025-10-01T21:44:29.267Z] An error occurred in the replication function: orchestrate_replication() got an unexpected keyword argument 'config'
[2025-10-01T21:44:29.161Z] Replication configuration loaded successfully[2025-10-01T21:44:29.414Z] Executed 'Functions.replication_fuction' (Failed, Id=8e88c773-8165-4d0f-a55c-186fe45c2581, Duration=3543ms)

[2025-10-01T21:44:29.818Z] System.Private.CoreLib: Exception while executing function: Functions.replication_fuction. System.Private.CoreLib: Result: Failure
Exception: TypeError: orchestrate_replication() got an unexpected keyword argument 'config'
Stack:   File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\dispatcher.py", line 676, in _handle__invocation_request
    call_result = await self._loop.run_in_executor(
  File "C:\Python\Lib\concurrent\futures\thread.py", line 58, in run
    result = self.fn(*self.args, **self.kwargs)
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\dispatcher.py", line 1006, in _run_sync_func
    return ExtensionManager.get_sync_invocation_wrapper(context,
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\extension.py", line 211, in _raw_invocation_wrapper
    result = function(**args)
  File "C:\Users\u69819\Documents\DevOps\service_bus\cloud-platform-servicebus-replication\src\replication_fuction\__init__.py", line 27, in main
    orchestrate_replication(source_message=msg, config=config, logger=logger)
.
[2025-10-01T21:44:29.819Z] No Application Insights configuration found, using standard logging
[2025-10-01T21:44:30.092Z] An error occurred in the replication function: orchestrate_replication() got an unexpected keyword argument 'config'
[2025-10-01T21:44:30.095Z] Executed 'Functions.replication_fuction' (Failed, Id=8e2e1cdc-c4b2-4e5c-93ef-114a35dc5633, Duration=4368ms)
[2025-10-01T21:44:30.096Z] System.Private.CoreLib: Exception while executing function: Functions.replication_fuction. System.Private.CoreLib: Result: Failure
Exception: TypeError: orchestrate_replication() got an unexpected keyword argument 'config'
Stack:   File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\dispatcher.py", line 676, in _handle__invocation_request
    call_result = await self._loop.run_in_executor(
  File "C:\Python\Lib\concurrent\futures\thread.py", line 58, in run
    result = self.fn(*self.args, **self.kwargs)
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\dispatcher.py", line 1006, in _run_sync_func
    return ExtensionManager.get_sync_invocation_wrapper(context,
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\extension.py", line 211, in _raw_invocation_wrapper
    result = function(**args)
  File "C:\Users\u69819\Documents\DevOps\service_bus\cloud-platform-servicebus-replication\src\replication_fuction\__init__.py", line 27, in main
    orchestrate_replication(source_message=msg, config=config, logger=logger)
.