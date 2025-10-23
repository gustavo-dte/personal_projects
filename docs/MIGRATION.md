# Azure Functions Structure Migration

## Overview
The project has been reorganized to follow Azure Functions best practices and improve the development workflow.

## Key Changes

### Folder Structure (OLD → NEW)
```
OLD Structure:
src/
├── main.py              # Entry point
├── config.py
├── message_utils.py
└── function.json

NEW Structure:
src/
├── __init__.py                     # Package marker
└── ServiceBusReplication/         # Azure Function App
    ├── __init__.py                # Entry point (was main.py)
    ├── function.json              # Function configuration
    ├── config.py
    ├── message_utils.py
    └── ...
```

### Import Changes
- **Old imports**: `from src.config import ReplicationConfig`
- **New imports**: `from src.ServiceBusReplication.config import ReplicationConfig`

### Testing Changes
- **Old coverage**: `pytest tests/ --cov=src`
- **New coverage**: `pytest tests/ --cov=src.ServiceBusReplication`

### CI/CD Changes
- Updated GitHub workflows to use new coverage path
- All test files updated with correct import paths
- Pre-commit hooks configuration remains the same

## Benefits of New Structure

1. **Azure Functions Compliance**: Follows Azure Functions package structure standards
2. **Better Organization**: Clear separation between function app and supporting modules
3. **Deployment Ready**: Structure is optimized for Azure Functions deployment
4. **Improved Testing**: More precise test coverage targeting
5. **Scalability**: Easier to add multiple functions in the future

## Migration Impact

✅ **All tests now pass** (29/29)  
✅ **Coverage improved to 81%** (exceeds 70% requirement)  
✅ **CI/CD pipelines updated**  
✅ **Documentation updated**  

## Developer Notes

- The main function logic is now in `src/ServiceBusReplication/__init__.py`
- All internal imports use relative paths (`from .config import ReplicationConfig`)
- Test files have been updated to use the new import structure
- The `function.json` file correctly references the new entry point

## Verification

To verify the new structure works correctly:

```bash
# Run all tests
pytest tests/ --cov=src.ServiceBusReplication -v

# Check import structure
python -c "from src.ServiceBusReplication import main; print('✅ Imports working')"

# Verify Azure Functions structure
test -f src/ServiceBusReplication/__init__.py && echo "✅ Entry point exists"
test -f src/ServiceBusReplication/function.json && echo "✅ Function config exists"
```

All tests should pass and coverage should be above 70%.