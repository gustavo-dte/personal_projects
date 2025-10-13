[2025-10-13T22:18:54.477Z]   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
[2025-10-13T22:18:54.477Z]   File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\main.py", line 9, in <module>
[2025-10-13T22:18:54.478Z]     from .error_handlers import (
[2025-10-13T22:18:54.479Z] ImportError: cannot import name 'handle_servicebus_error' from '__app__.src.error_handlers' (C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\error_handlers.py)
[2025-10-13T22:18:53.061Z] Error: cannot import name 'handle_servicebus_error' from '__app__.src.error_handlers' (C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\error_handlers.py), Cannot find module. Please check the requirements.txt file for the missing module. For more info, please refer the troubleshooting guide: https://aka.ms/functions-modulenotfound. Current sys.path: ['C:\\Program Files\\Microsoft\\Azure Functions Core Tools\\workers\\python\\3.11\\WINDOWS\\X64', 'C:\\Program Files\\Microsoft\\Azure Functions Core Tools\\workers\\python\\3.11\\WINDOWS\\X64', 'C:\\Python\\python311.zip', 'C:\\Python\\DLLs', 'C:\\Python\\Lib', 'C:\\Python', 'C:\\Users\\u69819\\Documents\\DevOps\\service_bus\\personal\\personal_projects\\src\\.venv', 'C:\\Users\\u69819\\Documents\\DevOps\\service_bus\\personal\\personal_projects\\src\\.venv\\Lib\\site-packages', 'C:\\Users\\u69819\\Documents\\DevOps\\service_bus\\personal\\personal_projects']
Traceback (most recent call last):
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
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\main.py", line 9, in <module>
    from .error_handlers import (
ImportError: cannot import name 'handle_servicebus_error' from '__app__.src.error_handlers' (C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\error_handlers.py)

[2025-10-13T22:18:54.486Z] Result: Failure
Exception: ImportError: cannot import name 'handle_servicebus_error' from '__app__.src.error_handlers' (C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\error_handlers.py). Cannot find module. Please check the requirements.txt file for the missing module. For more info, please refer the troubleshooting guide: https://aka.ms/functions-modulenotfound. Current sys.path: ['C:\\Program Files\\Microsoft\\Azure Functions Core Tools\\workers\\python\\3.11\\WINDOWS\\X64', 'C:\\Program Files\\Microsoft\\Azure Functions Core Tools\\workers\\python\\3.11\\WINDOWS\\X64', 'C:\\Python\\python311.zip', 'C:\\Python\\DLLs', 'C:\\Python\\Lib', 'C:\\Python', 'C:\\Users\\u69819\\Documents\\DevOps\\service_bus\\personal\\personal_projects\\src\\.venv', 'C:\\Users\\u69819\\Documents\\DevOps\\service_bus\\personal\\personal_projects\\src\\.venv\\Lib\\site-packages', 'C:\\Users\\u69819\\Documents\\DevOps\\service_bus\\personal\\personal_projects']
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
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\main.py", line 9, in <module>
    from .error_handlers import (