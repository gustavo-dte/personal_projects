ruff check...............................................................Failed
- hook id: ruff-check
- exit code: 1

src\error_handlers.py:65:89: E501 Line too long (103 > 88)
   |
63 |     )
64 |     raise ResourceNotFoundError(
65 |         f"Could not find destination topic '{destination_topic}': {sanitize_error_message(str(error))}"
   |                                                                                         ^^^^^^^^^^^^^^^ E501
66 |     ) from error
   |

src\error_handlers.py:169:89: E501 Line too long (92 > 88)
    |
167 |     )
168 |     raise ReplicationError(
169 |         f"Unexpected error during message replication: {sanitize_error_message(str(error))}"
    |                                                                                         ^^^^ E501
170 |     ) from error
    |

Found 2 errors.