mypy.....................................................................Failed
- hook id: mypy
- exit code: 1

src\config.py:134: error: Function is missing a return type annotation  [no-untyped-def]
src\config.py:180: error: Redundant cast to "str"  [redundant-cast]
src\config.py:183: error: Redundant cast to "str"  [redundant-cast]
src\retry_utils.py:19: error: Function is missing a type annotation  [no-untyped-def]
src\retry_utils.py:28: error: Function is missing a type annotation  [no-untyped-def]
src\retry_utils.py:30: error: Function is missing a type annotation  [no-untyped-def]
src\main.py:72: error: Function is missing a type annotation  [no-untyped-def]
src\main.py:126: error: Function is missing a type annotation for one or more arguments  [no-untyped-def]
src\main.py:138: error: Function is missing a type annotation  [no-untyped-def]
src\main.py:150: error: Function is missing a type annotation  [no-untyped-def]
src\main.py:178: error: Function is missing a type annotation  [no-untyped-def]
src\main.py:185: error: Function is missing a type annotation  [no-untyped-def]
Found 12 errors in 3 files (checked 5 source files)