[2025-10-13T21:01:42.150Z] Host lock lease acquired by instance ID '000000000000000000000000EE44FDF1'.[2025-10-13T21:01:42.565Z] Worker failed to load function: 'src' with functionId: '8c6f87bf-29d7-4c25-a2fa-389e3ed768d9'.

[2025-10-13T21:01:42.702Z] Result: Failure
Exception: AttributeError: 'ReplicationConfig' object has no attribute 'has_app_insights_config'
Stack:   File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\dispatcher.py", line 546, in _handle__function_load_request
    func = loader.load_function(
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\utils\wrappers.py", line 44, in call
    return func(*args, **kwargs)
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\loader.py", line 220, in load_function
    mod = importlib.import_module(fullmodname)
  File "C:\Python\Lib\importlib\__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\main.py", line 38, in <module>  
    app_logger = configure_logger()
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\logging_utils.py", line 47, in configure_logger
    (config and config.has_app_insights_config) if config else False
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\.venv\Lib\site-packages\pydantic\main.py", line 1026, in __getattr__
    raise AttributeError(f'{type(self).__name__!r} object has no attribute {item!r}')
.
[2025-10-13T21:01:43.762Z] Executed 'Functions.src' (Failed, Id=33b3fcff-a141-47c6-8cf8-a711eaa9322e, Duration=4809ms)
[2025-10-13T21:01:43.978Z] System.Private.CoreLib: Exception while executing function: Functions.src. System.Private.CoreLib: Result: Failure
Exception: AttributeError: 'ReplicationConfig' object has no attribute 'has_app_insights_config'
Stack:   File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\dispatcher.py", line 546, in _handle__function_load_request
    func = loader.load_function(
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\utils\wrappers.py", line 44, in call
    return func(*args, **kwargs)
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\loader.py", line 220, in load_function
    mod = importlib.import_module(fullmodname)
  File "C:\Python\Lib\importlib\__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\main.py", line 38, in <module>  
    app_logger = configure_logger()
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\logging_utils.py", line 47, in configure_logger
    (config and config.has_app_insights_config) if config else False
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\.venv\Lib\site-packages\pydantic\main.py", line 1026, in __getattr__
    raise AttributeError(f'{type(self).__name__!r} object has no attribute {item!r}')