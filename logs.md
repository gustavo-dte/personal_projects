ruff check...............................................................Failed
- hook id: ruff-check
- exit code: 1

src\config.py:136:89: E501 Line too long (93 > 88)
    |
134 |     def validate_connection_config(self):
135 |         """Validate that required connection strings are provided."""
136 |         # For dynamic replication, both primary and secondary connection strings are required      
    |                                                                                         ^^^^^ E501 
137 |         if not self.primary_conn_str:
138 |             raise ConfigError(
    |

src\main.py:105:88: E501 Line too long (89 > 88)
    |
103 |                 receiver.complete_message(msg)
104 |                 logger.info(
105 |                     f"✅ Replicated message {correlation_id} from {topic}/{subscription}"
    |                                                                                         ^ E501     
106 |                 )
    |

src\main.py:112:88: E501 Line too long (103 > 88)
    |
110 |                 receiver.abandon_message(msg)
111 |                 logger.error(
112 |                     f"❌ Failed to replicate message {correlation_id} from {topic}/{subscription}: {e}"
    |                                                                                         ^^^^^^^^^^^^^^^ E501
113 |                 )
    |

src\message_utils.py:151:18: C408 Unnecessary `dict()` call (rewrite as a literal)
    |
150 |       # --- TTL handling (avoid NoneType errors) -------------------------------
151 |       msg_kwargs = dict(
    |  __________________^
152 | |         body=processed_body,
153 | |         application_properties=cast(Any, enhanced_properties),
154 | |         content_type=final_content_type,
155 | |         correlation_id=correlation_id,
156 | |         subject=getattr(source_message, "subject", None),
157 | |         session_id=getattr(source_message, "session_id", None),
158 | |         to=getattr(source_message, "to", None),
159 | |         reply_to=getattr(source_message, "reply_to", None),
160 | |         reply_to_session_id=getattr(source_message, "reply_to_session_id", None),
161 | |         partition_key=getattr(source_message, "partition_key", None),
162 | |         scheduled_enqueue_time_utc=getattr(
163 | |             source_message, "scheduled_enqueue_time_utc", None
164 | |         ),
165 | |         message_id=new_message_id,
166 | |     )
    | |_____^ C408
167 |
168 |       # Only set TTL if valid and numeric
    |
    = help: Rewrite as a literal

src\message_utils.py:169:36: UP038 Use `X | Y` in `isinstance` call instead of `(X, Y)`
    |
168 |     # Only set TTL if valid and numeric
169 |     if ttl_seconds is not None and isinstance(ttl_seconds, (int, float)):
    |                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ UP038
170 |         msg_kwargs["time_to_live"] = timedelta(seconds=int(ttl_seconds))
    |
    = help: Convert to `X | Y`

Found 5 errors.
No fixes available (2 hidden fixes can be enabled with the `--unsafe-fixes` option).

ruff check...............................................................Passed
ruff format..............................................................Passed
mypy.....................................................................Failed
- hook id: mypy
- exit code: 1

src\config.py:134: error: Function is missing a return type annotation  [no-untyped-def]
src\config.py:179: error: Redundant cast to "str"  [redundant-cast]
src\config.py:182: error: Redundant cast to "str"  [redundant-cast]
src\retry_utils.py:19: error: Function is missing a type annotation  [no-untyped-def]
src\retry_utils.py:28: error: Function is missing a type annotation  [no-untyped-def]
src\retry_utils.py:30: error: Function is missing a type annotation  [no-untyped-def]
src\main.py:72: error: Function is missing a type annotation  [no-untyped-def]
src\main.py:119: error: Function is missing a type annotation for one or more arguments  [no-untyped-def]
src\main.py:131: error: Function is missing a type annotation  [no-untyped-def]
src\main.py:143: error: Function is missing a type annotation  [no-untyped-def]
src\main.py:171: error: Function is missing a type annotation  [no-untyped-def]
src\main.py:178: error: Function is missing a type annotation  [no-untyped-def]
Found 12 errors in 3 files (checked 5 source files)