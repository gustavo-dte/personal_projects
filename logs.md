63170, DeliveryCount: 9, EnqueuedTimeUtc: 2025-10-01T15:30:29.2200000+00:00, LockedUntilUtc: 2025-10-01T21:17:18.9170000+00:00, SessionId: $sessionId
[2025-10-01T21:16:21.012Z] Executed 'Functions.replication_fuction' (Failed, Id=2f27e29c-0cce-4ee3-bd4c-7ad4c33f80b2, Duration=4ms)
[2025-10-01T21:16:21.012Z] System.Private.CoreLib: Exception while executing function: Functions.replication_fuction. System.Private.CoreLib: Result: Failure
Exception: ModuleNotFoundError: No module named 'shared.constantsconstants'. Cannot find module. Please check the requirements.txt file for the missing module. For more info, please refer the troubleshooting guide: https://aka.ms/functions-modulenotfound. Current sys.path: ['C:\\Program Files\\Microsoft\\Azure Functions Core Tools\\workers\\python\\3.11\\WINDOWS\\X64', 'C:\\Program Files\\Microsoft\\Azure Functions Core Tools\\workers\\python\\3.11\\WINDOWS\\X64', 'C:\\Python\\python311.zip', 'C:\\Python\\DLLs', 'C:\\Python\\Lib', 'C:\\Python', 'C:\\Users\\u69819\\Documents\\DevOps\\service_bus\\cloud-platform-servicebus-replication\\src\\.venv', 'C:\\Users\\u69819\\Documents\\DevOps\\service_bus\\cloud-platform-servicebus-replication\\src\\.venv\\Lib\\site-packages', 'C:\\Users\\u69819\\Documents\\DevOps\\service_bus\\cloud-platform-servicebus-replication\\src']
Stack:   File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\dispatcher.py", line 546, in _handle__function_load_request
    func = loader.load_function(
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\utils\wrappers.py", line 49, in call
    raise extend_exception_message(e, message)
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\utils\wrappers.py", line 44, in call
    return func(*args, **kwargs)
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\loader.py", line 220, in load_function
    mod = importlib.import_module(fullmodname)
  File "C:\Python\Lib\importlib\__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
  File "C:\Users\u69819\Documents\DevOps\service_bus\cloud-platform-servicebus-replication\src\replication_fuction\__init__.py", line 3, in <module>
    from shared.main import (
  File "C:\Users\u69819\Documents\DevOps\service_bus\cloud-platform-servicebus-replication\src\shared\main.py", line 22, in <module>
    from shared.constantsconstants import ALERT_SEVERITY_CRITICAL, ALERT_SEVERITY_HIGH