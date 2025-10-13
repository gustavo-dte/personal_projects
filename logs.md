[2025-10-13T22:07:40.960Z] 1 functions loaded
[2025-10-13T22:07:41.133Z] Generating 1 job function(s)[2025-10-13T22:07:41.157Z] Received WorkerLoadRequest, request ID dc41586e-f616-4d37-90b1-6b61f88ef6bc, function_id: 4086a84e-39d7-4047-9d2e-1404536804a4,function_name: src, function_app_directory : C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src
[2025-10-13T22:07:41.220Z] Worker failed to load function: 'src' with functionId: '4086a84e-39d7-4047-9d2e-1404536804a4'.
[2025-10-13T22:07:41.222Z] Result: Failure
Exception: SyntaxError: name 'app_logger' is used prior to global declaration (main.py, line 36)
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
  File "<frozen importlib._bootstrap_external>", line 936, in exec_module
  File "<frozen importlib._bootstrap_external>", line 1074, in get_code
  File "<frozen importlib._bootstrap_external>", line 1004, in source_to_code
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
.
[2025-10-13T22:07:41.159Z] Worker process started and initialized.

[2025-10-13T22:07:41.492Z] Found the following functions:
[2025-10-13T22:07:41.531Z] Host.Functions.src
[2025-10-13T22:07:41.688Z] 
[2025-10-13T22:07:41.886Z] Initializing function HTTP routes[2025-10-13T22:07:41.887Z] HttpOptions

[2025-10-13T22:07:41.897Z] No HTTP routes mapped
[2025-10-13T22:07:41.899Z] {
[2025-10-13T22:07:41.900Z]
[2025-10-13T22:07:41.900Z]   "DynamicThrottlesEnabled": false,
[2025-10-13T22:07:41.905Z]   "EnableChunkedRequestBinding": false,[2025-10-13T22:07:41.909Z] Host initialized (7379ms)

[2025-10-13T22:07:41.914Z]   "MaxConcurrentRequests": -1,

Functions:
[2025-10-13T22:07:42.245Z]   "MaxOutstandingRequests": -1,

        src: timerTrigger
[2025-10-13T22:07:42.249Z]   "RoutePrefix": "api"

[2025-10-13T22:07:42.253Z] }