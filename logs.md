mypy.....................................................................Failed
- hook id: mypy
- exit code: 1

src\main.py:59: error: Argument "dest_conn" to "process_subscription_messages" has incompatible type "str | None"; expected "str"  [arg-type]
src\main.py:148: error: Argument 2 to "replicate_message_to_destination" has incompatible type "str | None"; expected "str"  [arg-type]
src\main.py:174: error: Argument "correlation_id" to "create_replicated_message" has incompatible type "str | None"; expected "str"  [arg-type]
src\main.py:196: error: Argument 2 to "handle_unexpected_error" has incompatible type "str | None"; expected "str"  [arg-type]
Found 4 errors in 1 file (checked 5 source files)