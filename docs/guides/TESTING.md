# Testing Guide

Complete guide for testing the Supplier Invoice Loader application.

---

## Quick Start

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

---

## Test Organization

### Test Structure

```
tests/
├── __init__.py              # Test package init
├── conftest.py              # Shared fixtures
├── README.md                # Test documentation
│
├── test_config.py           # Configuration tests
├── test_notifications.py    # Email notification tests
├── test_extraction.py       # PDF extraction tests
├── test_monitoring.py       # Monitoring/metrics tests
├── test_api.py              # FastAPI endpoint tests
│
└── samples/                 # Test PDF files
    ├── README.md
    └── .gitkeep
```

### Test Categories

**Unit Tests** (fast, isolated):
- Test individual functions
- Mock external dependencies
- No database, no network, no files
- Run on every commit

**Integration Tests** (slower, realistic):
- Test multiple components together
- May use real database (temporary)
- May use real files
- Run before deployment

**End-to-End Tests** (slowest, full workflow):
- Test entire application flow
- Real API calls, real processing
- Run before major releases

---

## Running Tests

### Basic Commands

```bash
# All tests
pytest

# Verbose output
pytest -v

# Very verbose (show print statements)
pytest -vv -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Run specific file
pytest tests/test_config.py

# Run specific test
pytest tests/test_config.py::test_config_imports

# Run tests matching pattern
pytest -k "config"
pytest -k "not slow"
```

### By Category

```bash
# Unit tests only
pytest -m unit

# Integration tests (may require --run-integration flag)
pytest -m integration --run-integration

# Exclude slow tests
pytest -m "not slow"

# Only slow tests
pytest -m slow
```

### With Coverage

```bash
# Basic coverage
pytest --cov=.

# HTML report
pytest --cov=. --cov-report=html

# Terminal report with missing lines
pytest --cov=. --cov-report=term-missing

# XML report (for CI)
pytest --cov=. --cov-report=xml

# Coverage for specific module
pytest --cov=notifications tests/test_notifications.py
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4

# Run tests in parallel (auto-detect cores)
pytest -n auto
```

---

## Writing Tests

### Basic Test

```python
def test_something():
    """Test that something works"""
    result = my_function()
    assert result == expected_value
```

### Test with Fixture

```python
def test_with_fixture(sample_invoice_data):
    """Test using shared fixture"""
    assert sample_invoice_data.invoice_number == "2025001"
```

### Test with Mock

```python
from unittest.mock import Mock, patch

@patch('mymodule.external_api')
def test_with_mock(mock_api):
    """Test with mocked external call"""
    mock_api.return_value = {"status": "success"}
    
    result = my_function()
    
    assert result is not None
    mock_api.assert_called_once()
```

### Parametrized Test

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("test", "TEST"),
])
def test_uppercase(input, expected):
    """Test with multiple input/output pairs"""
    assert input.upper() == expected
```

### Test Exceptions

```python
def test_raises_exception():
    """Test that function raises expected exception"""
    with pytest.raises(ValueError):
        my_function(invalid_input)
```

### Async Test

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async function"""
    result = await my_async_function()
    assert result is not None
```

---

## Test Fixtures

### Built-in Fixtures

Fixtures defined in `conftest.py`:

#### test_data_dir
```python
def test_with_data_dir(test_data_dir):
    """Use test data directory"""
    sample = test_data_dir / "sample.pdf"
    assert sample.exists()
```

#### sample_invoice_data
```python
def test_invoice_data(sample_invoice_data):
    """Pre-populated invoice data"""
    assert sample_invoice_data.invoice_number == "2025001"
    assert len(sample_invoice_data.items) == 2
```

#### mock_config
```python
def test_with_config(mock_config):
    """Mocked configuration"""
    assert mock_config.API_KEY == "test-api-key-12345"
```

#### temp_database
```python
def test_with_db(temp_database):
    """Temporary SQLite database"""
    import sqlite3
    conn = sqlite3.connect(str(temp_database))
    # Use database
    conn.close()
```

#### api_client
```python
def test_endpoint(api_client):
    """FastAPI test client"""
    response = api_client.get("/health")
    assert response.status_code == 200
```

### Custom Fixtures

Create custom fixtures in conftest.py:

```python
@pytest.fixture
def my_fixture():
    """Custom fixture"""
    # Setup
    resource = create_resource()
    
    yield resource  # Provide to test
    
    # Teardown
    resource.cleanup()
```

---

## Mocking

### Mock External API

```python
from unittest.mock import Mock, patch

@patch('requests.get')
def test_api_call(mock_get):
    """Mock HTTP request"""
    mock_get.return_value.json.return_value = {"data": "test"}
    mock_get.return_value.status_code = 200
    
    result = fetch_data()
    
    assert result["data"] == "test"
    mock_get.assert_called_with("https://api.example.com/data")
```

### Mock SMTP Server

```python
@patch('smtplib.SMTP')
def test_email(mock_smtp):
    """Mock email sending"""
    mock_server = Mock()
    mock_smtp.return_value = mock_server
    
    send_email("test@example.com", "Subject", "Body")
    
    mock_server.send_message.assert_called_once()
```

### Mock File System

```python
from unittest.mock import mock_open, patch

@patch('builtins.open', mock_open(read_data='test data'))
def test_read_file():
    """Mock file reading"""
    content = read_file('test.txt')
    assert content == 'test data'
```

---

## Coverage Goals

### Target Coverage

- **Overall:** 80%+
- **Critical modules:** 90%+
  - config.py
  - notifications.py
  - monitoring.py
  
- **Important modules:** 80%+
  - main.py
  - database.py
  - extractors/
  
- **Lower priority:** 60%+
  - isdoc.py (complex XML)
  - env_loader.py (simple)

### Checking Coverage

```bash
# Generate report
pytest --cov=. --cov-report=html

# View in browser
open htmlcov/index.html

# Coverage by file
pytest --cov=. --cov-report=term-missing

# Example output:
# Name                    Stmts   Miss  Cover   Missing
# -----------------------------------------------------
# config.py                  45      3    93%   78, 92, 105
# notifications.py          120     15    88%   
# main.py                   200     60    70%   
```

### Improving Coverage

Focus on:
1. **Untested functions** - Add basic test
2. **Error paths** - Test exception handling
3. **Edge cases** - Test with None, empty, invalid inputs
4. **Branch coverage** - Test if/else branches

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Run tests before commit

pytest -x --tb=short

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Testing Best Practices

### 1. Test One Thing

```python
# Good
def test_config_has_api_key():
    assert hasattr(config, 'API_KEY')

def test_api_key_is_string():
    assert isinstance(config.API_KEY, str)

# Bad
def test_config():
    assert hasattr(config, 'API_KEY')
    assert isinstance(config.API_KEY, str)
    assert len(config.API_KEY) > 0
    # ... too many assertions
```

### 2. Use Descriptive Names

```python
# Good
def test_invoice_extraction_handles_missing_pdf():
    """Test that extractor returns None for missing file"""
    result = extract_invoice_data('/nonexistent.pdf')
    assert result is None

# Bad
def test_extraction():
    result = extract_invoice_data('/nonexistent.pdf')
    assert result is None
```

### 3. Arrange-Act-Assert

```python
def test_calculate_total():
    # Arrange
    items = [10, 20, 30]
    
    # Act
    total = sum(items)
    
    # Assert
    assert total == 60
```

### 4. Test Edge Cases

```python
def test_parse_decimal_edge_cases():
    assert parse_decimal(None) is None
    assert parse_decimal("") is None
    assert parse_decimal("0") == Decimal("0")
    assert parse_decimal("-100") == Decimal("-100")
```

### 5. Don't Test Implementation

```python
# Bad - tests implementation details
def test_uses_regex():
    assert hasattr(extractor, '_regex_pattern')
    assert extractor._regex_pattern.match("test")

# Good - tests behavior
def test_extracts_invoice_number():
    result = extractor.extract("Invoice: 12345")
    assert result.invoice_number == "12345"
```

---

## Debugging Tests

### Show Print Statements

```bash
pytest -s
# or
pytest -vv -s
```

### Drop to Debugger on Failure

```bash
pytest --pdb
```

### Use Breakpoints

```python
def test_something():
    result = function()
    import pdb; pdb.set_trace()  # Breakpoint
    assert result == expected
```

### Better with ipdb

```bash
pip install ipdb
```

```python
def test_something():
    import ipdb; ipdb.set_trace()
    # Full ipython debugger
```

---

## Common Issues

### Tests Pass Locally, Fail in CI

**Causes:**
- Different Python versions
- Missing dependencies
- Timing issues
- Environment variables not set

**Solutions:**
- Pin Python version in CI
- Ensure all dependencies in requirements-dev.txt
- Use `time.sleep()` or `pytest-timeout`
- Set env vars in CI config

### ImportError

**Problem:**
```
ImportError: cannot import name 'config'
```

**Solution:**
```bash
# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or install in dev mode
pip install -e .
```

### Database Locked

**Problem:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
- Use `temp_database` fixture
- Close connections in teardown
- Use separate DB for each test

---

## Performance Testing

### Timing Tests

```python
import time

def test_performance():
    """Test should complete in < 1 second"""
    start = time.time()
    
    result = expensive_function()
    
    duration = time.time() - start
    assert duration < 1.0
```

### Benchmark with pytest-benchmark

```bash
pip install pytest-benchmark
```

```python
def test_benchmark(benchmark):
    """Benchmark function performance"""
    result = benchmark(my_function, arg1, arg2)
    assert result is not None
```

---

## Resources

- **pytest:** https://docs.pytest.org/
- **coverage.py:** https://coverage.readthedocs.io/
- **unittest.mock:** https://docs.python.org/3/library/unittest.mock.html
- **FastAPI testing:** https://fastapi.tiangolo.com/tutorial/testing/
- **Testing best practices:** https://docs.python-guide.org/writing/tests/

---

## Support

For testing issues:
1. Check this guide
2. Review tests/README.md
3. Check existing tests for examples
4. Contact: support@icc.sk

---

**Happy Testing! 🧪**