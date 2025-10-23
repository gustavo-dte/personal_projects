# Development Guide

## Getting Started with Development

### Prerequisites
- Python 3.11+
- Git
- Azure Functions Core Tools (for local testing)

### Initial Setup

1. **Clone and set up environment** (see main README)
2. **Install development dependencies** (already covered in main installation)
3. **Configure pre-commit hooks** (already set up during installation)

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code standards below

3. **Run quality checks before committing**
   ```bash
   # Type checking, linting, and formatting (pre-commit hooks run automatically)
   mypy src/ tests/
   ruff check src/ tests/
   ruff format src/ tests/
   pytest tests/ --cov=src.ServiceBusReplication
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```
   > Pre-commit hooks will run automatically and prevent commits with issues

5. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Standards

### Security Guidelines
- **Secure Logging**: Never log sensitive information such as:
  - Connection strings or access keys
  - Message content or payloads
  - Full correlation IDs (use `truncate_correlation_id()`)
  - Raw exception messages (use `sanitize_error_message()`)
- **Error Handling**: Always sanitize error messages before logging
- **Data Validation**: Use Pydantic models for configuration validation
- **Secret Management**: Store sensitive configuration in Azure Key Vault when possible

### Type Safety
- **100% mypy compliance required** - All code must pass type checking
- Use type hints for all function parameters and return values
- Use `from __future__ import annotations` for forward references

### Code Quality
- **Ruff linting** - Follow all ruff rules (configured in `pyproject.toml`)
- **Code formatting** - Use ruff format (runs automatically via pre-commit)
- **Import organization** - Ruff handles import sorting and organization

### Testing Requirements
- **Minimum 70% test coverage** (currently at 82%)
- **Unit tests required** for all new functions and classes
- **Integration tests** for complex workflows
- **Mock external dependencies** (Azure Service Bus, etc.)

### Documentation
- **Docstrings required** for all public functions and classes
- Use Google-style docstrings
- Include type information in docstrings where helpful
- Update README/docs when adding new features

## Testing

### Running Tests
```bash
# Run all tests with coverage
pytest tests/ --cov=src.ServiceBusReplication --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/main_test.py -v

# Run tests matching a pattern
pytest tests/ -k "test_message" -v
```

### Test Structure
```
tests/
├── main_test.py                  # Main functionality tests
├── error_handlers_test.py        # Error handling tests  
├── message_utils_test.py         # Message utilities tests
├── retry_utils_test.py           # Retry mechanism tests
├── exceptions_test.py            # Custom exception tests
├── constants_test.py             # Constants tests
└── conftest.py                  # Test fixtures and configuration
```

### Writing Tests
- Use descriptive test names: `test_should_retry_on_transient_error()`
- Follow AAA pattern: Arrange, Act, Assert
- Mock external dependencies using `unittest.mock`
- Test both success and failure scenarios
- Include edge cases and boundary conditions

Example:
```python
def test_should_enhance_message_with_replication_metadata():
    # Arrange
    original_message = ServiceBusReceivedMessage(...)
    correlation_id = "test-correlation-123"
    
    # Act
    enhanced_message = enhance_message(original_message, correlation_id)
    
    # Assert
    assert enhanced_message.application_properties["x-replication-correlation-id"] == correlation_id
    assert enhanced_message.application_properties["x-original-message-id"] == original_message.message_id
```

## Local Development

### Running Locally
```bash
# Start the Azure Functions runtime
func start --python

# The function will run on http://localhost:7071
# Timer trigger will execute every 30 seconds
```

### Environment Setup
- Copy `local.settings.example.json` to `local.settings.json`
- Fill in your Service Bus connection strings
- Configure other settings as needed (see [Configuration Guide](./CONFIGURATION.md))

### Debugging
- Use VS Code with the Azure Functions extension
- Set breakpoints in your code
- Use the integrated debugger to step through execution
- Check Azure Functions logs for runtime information

## Project Structure

### Azure Functions Organization
```
src/
├── __init__.py                           # Package marker for src
└── ServiceBusReplication/               # Azure Function App
    ├── __init__.py                      # Main Azure Function entry point & timer trigger
    ├── function.json                    # Azure Functions timer trigger configuration
    ├── config.py                        # Configuration management with Pydantic v2
    ├── message_utils.py                 # Message processing & enhancement utilities
    ├── retry_utils.py                   # Retry logic with exponential backoff
    ├── logging_utils.py                 # Centralized logging with Azure Monitor
    ├── error_handlers.py                # Comprehensive error handling utilities
    ├── exceptions.py                    # Custom exception classes
    └── constants.py                     # Application constants

tests/                                   # Unit tests
├── main_test.py                         # Main functionality tests
├── config_test.py                       # Configuration tests
├── message_utils_test.py                # Message utilities tests
├── retry_utils_test.py                  # Retry logic tests
├── error_handlers_test.py               # Error handling tests
├── exceptions_test.py                   # Exception tests
└── constants_test.py                    # Test constants

host.json                               # Azure Functions host configuration
requirements.txt                        # Python dependencies
local.settings.json                     # Local development settings (not in git)
```

### Azure Functions Structure Notes
- **`src/ServiceBusReplication/`**: Contains the Azure Function implementation
- **`__init__.py`**: Main entry point defined by `function.json` scriptFile
- **`function.json`**: Defines the timer trigger (runs every 30 seconds)
- **Imports**: All modules use relative imports within the ServiceBusReplication package

### Key Design Patterns
- **Configuration as Code**: All settings via environment variables
- **Error Isolation**: Comprehensive error handling with correlation IDs
- **Retry Logic**: Exponential backoff for transient failures
- **Observability**: Structured logging with correlation tracking
- **Type Safety**: Pydantic models for configuration validation

## Contributing Guidelines

### Pull Request Process
1. **Fork the repository** (for external contributors)
2. **Create a feature branch** from `main`
3. **Make your changes** following code standards
4. **Add/update tests** for new functionality
5. **Update documentation** if needed
6. **Run full test suite** and ensure all checks pass
7. **Submit pull request** with clear description

### Pull Request Requirements
- ✅ All CI checks must pass (tests, linting, type checking)
- ✅ Code coverage must not decrease
- ✅ All new code must have corresponding tests
- ✅ Documentation must be updated for new features
- ✅ Commit messages should follow conventional commits format

### Code Review Process
- All PRs require at least one approval
- Address all review comments before merging
- Maintain a clean commit history (squash if necessary)
- Update PR description with any significant changes

## Release Process

### Version Management
- Follow semantic versioning (SemVer)
- Update version in relevant files
- Create git tags for releases

### Release Checklist
1. ✅ All tests pass
2. ✅ Documentation is up to date
3. ✅ CHANGELOG is updated
4. ✅ Version number is bumped
5. ✅ Create release tag
6. ✅ Deploy to staging for validation
7. ✅ Deploy to production

## Getting Help

### Common Issues
- Check the [Troubleshooting Guide](./TROUBLESHOOTING.md)
- Review existing GitHub issues
- Check Azure Functions and Service Bus documentation

### Community Support
- Create GitHub issues for bugs or feature requests
- Use discussions for questions and general help
- Follow contribution guidelines for PRs