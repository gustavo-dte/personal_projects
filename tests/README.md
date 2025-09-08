# Testing

This project follows Python best practices with a proper src/tests structure.

## Project Structure

```
project_root/
├── src/                          # Production code
│   ├── __init__.py
│   ├── main.py                   # Azure Function entry point
│   ├── config.py                 # Configuration management
│   ├── constants.py              # Application constants
│   ├── error_handlers.py         # Error handling logic
│   ├── exceptions.py             # Custom exceptions
│   ├── logging_utils.py          # Logging utilities
│   ├── message_utils.py          # Message processing utilities
│   └── retry_utils.py            # Retry logic utilities
└── tests/                        # Test code
    ├── __init__.py
    └── test_main.py               # Unit tests
```

## Running Tests

From the project root directory:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_main.py

# Run specific test class
pytest tests/test_main.py::TestConfigurationLoading

# Run specific test method
pytest tests/test_main.py::TestConfigurationLoading::test_load_and_validate_config_success
```

## Benefits of This Structure

### Clear Separation
- Distinguishes between production code (`src/`) and test code (`tests/`)
- Makes it easy to understand what code is shipped vs what is for testing

### Easier Deployment
- When packaging for Azure Functions, the `tests/` directory can be excluded
- Results in smaller, cleaner deployments

### Improved Import Management
- Tests import from the `src` package using absolute imports
- Ensures tests run against the properly packaged code
- Prevents accidental imports from local, uninstalled versions

### Standard Practice
- Follows widely adopted Python community conventions
- Makes the project familiar to other Python developers
- Compatible with standard tooling and CI/CD pipelines
