trim trailing whitespace.................................................Passed
ruff check...............................................................Failed
- hook id: ruff-check
- exit code: 1

tests\main_test.py:51:14: B017 Do not assert blind exception: `Exception`
   |
49 |         )
50 |
51 |         with pytest.raises(Exception):
   |              ^^^^^^^^^^^^^^^^^^^^^^^^ B017
52 |             mock_config()
   |

Found 1 error.

ruff check...............................................................Passed
ruff format..............................................................Passed
mypy.....................................................................Failed
- hook id: mypy
- exit code: 1

tests\exceptions_test.py:49: error: Statement is unreachable  [unreachable]
Found 1 error in 1 file (checked 5 source files)