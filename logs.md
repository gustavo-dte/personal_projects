For detailed output, run func with --verbose flag.

[2025-10-13T21:43:17.557Z] Host lock lease acquired by instance ID '000000000000000000000000EE44FDF1'.
[2025-10-13T21:43:20.259Z] Worker failed to load function: 'src' with functionId: 'd3058876-9700-4f03-8a1f-c9b9042702c8'.
[2025-10-13T21:43:20.261Z] Result: Failure
Exception: FunctionLoadError: cannot load the src function: the following parameters are declared in Python but not in function.json: {'msg'}
Stack:   File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\dispatcher.py", line 552, in _handle__function_load_request
    self._functions.add_function(
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\functions.py", line 392, in add_function
    input_types, output_types, _ = self.validate_function_params(
  File "C:\Program Files\Microsoft\Azure Functions Core Tools\workers\python\3.11\WINDOWS\X64\azure_functions_worker\functions.py", line 137, in validate_function_params
    raise FunctionLoadError(