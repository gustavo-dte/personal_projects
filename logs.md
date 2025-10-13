For detailed output, run func with --verbose flag.
[2025-10-13T21:47:31.609Z] Worker failed to load function: 'src' with functionId: '16363aa8-c631-4a79-8fd7-485d3a48928b'.
[2025-10-13T21:47:31.610Z] Result: Failure
Exception: FunctionLoadError: cannot load the src function: the following parameters are declared in Python but not in function.json: {'msg'}
Stack:   File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\dispatcher.py", line 552, in _handle__function_load_request
    self._functions.add_function(
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\functions.py", line 392, in add_function
    input_types, output_types, _ = self.validate_function_params(
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\functions.py", line 137, in validate_function_params
    raise FunctionLoadError(