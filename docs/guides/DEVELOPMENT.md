# Development Guide

Guide for developers working on Supplier Invoice Loader.

---

## Quick Start for Developers

### 1. Clone Repository

```bash
git clone https://github.com/rauschiccsk/supplier_invoice_loader.git
cd supplier_invoice_loader
git checkout v2.0-multi-customer
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install development dependencies
pip install --upgrade pip
pip install -r requirements-dev.txt
```

### 3. Configure Application

```bash
# Copy config template
cp config_template.py config_customer.py

# Copy environment template
cp .env.example .env

# Edit both files with your development values
```

### 4. Run Application

```bash
# Start development server (with auto-reload)
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access Documentation

- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

---

## Development Workflow

### Before Making Changes

```bash
# Update from main branch
git pull origin v2.0-multi-customer

# Create feature branch
git checkout -b feature/your-feature-name

# Ensure dependencies are current
pip install -r requirements-dev.txt
```

### While Developing

**Format code automatically:**
```bash
# Format all Python files
black .

# Sort imports
isort .
```

**Check code quality:**
```bash
# Lint
flake8 .

# Type check
mypy .

# Security scan
bandit -r .
```

**Run tests:**
```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific test file
pytest tests/test_extraction.py

# Watch mode (runs tests on file changes)
pytest-watch
```

### Before Committing

**Pre-commit checklist:**

```bash
# 1. Format and lint
black . && isort . && flake8 .

# 2. Type check
mypy .

# 3. Run tests
pytest

# 4. Security check
safety check
bandit -r .

# 5. Check for secrets
git diff  # Review changes, ensure no API keys/passwords

# 6. Commit
git add .
git commit -m "feat: your descriptive commit message"
```

**Commit message format:**
```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(extraction): add support for new supplier format
fix(notifications): resolve SMTP timeout issue
docs(readme): update installation instructions
```

### After Committing

```bash
# Push to GitHub
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# Request review from team
```

---

## Project Structure

```
supplier_invoice_loader/
├── main.py                 # FastAPI application entry point
├── config.py               # Config loader
├── config_template.py      # Config template
├── config_customer.py      # Customer-specific config (gitignored)
├── database.py             # SQLite database operations
├── models.py               # Pydantic data models
├── isdoc.py                # ISDOC XML generation
├── notifications.py        # Email alerting system
├── monitoring.py           # Health checks and metrics
├── env_loader.py           # Environment variables loader
│
├── extractors/             # PDF extraction modules
│   ├── __init__.py
│   ├── base_extractor.py   # Abstract base class
│   ├── ls_extractor.py     # L&Š specific extractor
│   └── generic_extractor.py # Generic extractor template
│
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_extraction.py
│   ├── test_notifications.py
│   └── samples/            # Test PDF files
│
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── pyproject.toml          # Tool configuration
├── .flake8                 # Flake8 configuration
├── mypy.ini                # MyPy configuration
├── .env                    # Environment variables (gitignored)
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
│
├── README.md               # Project overview
├── SECURITY.md             # Security guidelines
├── DEPLOYMENT_CHECKLIST.md # Deployment guide
├── TROUBLESHOOTING.md      # Common issues
├── MONITORING.md           # Monitoring setup
├── EMAIL_ALERTING.md       # Email alerts guide
├── N8N_WORKFLOW_SETUP.md   # n8n setup
├── PYTHON_SETUP.md         # Python environment guide
└── DEVELOPMENT.md          # This file
```

---

## Testing

### Running Tests

```bash
# All tests
pytest

# Verbose output
pytest -v

# Specific test file
pytest tests/test_extraction.py

# Specific test function
pytest tests/test_extraction.py::test_extract_invoice_number

# Tests matching pattern
pytest -k "extraction"

# Exclude slow tests
pytest -m "not slow"
```

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=. --cov-report=html

# Open in browser
# Windows: start htmlcov/index.html
# Linux/Mac: open htmlcov/index.html
```

### Writing Tests

**Example test:**

```python
# tests/test_extraction.py
import pytest
from extractors.ls_extractor import extract_invoice_data

def test_extract_invoice_number():
    """Test invoice number extraction"""
    # Arrange
    pdf_path = "tests/samples/sample_invoice.pdf"
    
    # Act
    result = extract_invoice_data(pdf_path)
    
    # Assert
    assert result is not None
    assert result.invoice_number == "2025001"

def test_extract_invalid_pdf():
    """Test handling of invalid PDF"""
    # Arrange
    pdf_path = "tests/samples/invalid.pdf"
    
    # Act
    result = extract_invoice_data(pdf_path)
    
    # Assert
    assert result is None

@pytest.mark.slow
def test_large_pdf_processing():
    """Test processing of large PDF (slow test)"""
    # This test is marked as slow
    pass
```

**Test fixtures:**

```python
@pytest.fixture
def sample_invoice_data():
    """Fixture providing sample invoice data"""
    from extractors.ls_extractor import InvoiceData
    
    return InvoiceData(
        invoice_number="2025001",
        issue_date="2025-01-15",
        total_amount=Decimal("1234.56")
    )

def test_with_fixture(sample_invoice_data):
    """Test using fixture"""
    assert sample_invoice_data.invoice_number == "2025001"
```

---

## Code Style

### Black (Formatter)

**Automatic formatting:**
```bash
# Format all files
black .

# Format specific file
black main.py

# Check without modifying
black --check .
```

**Configuration:** See `pyproject.toml` → `[tool.black]`

### isort (Import Sorter)

**Sort imports:**
```bash
# Sort all files
isort .

# Check only
isort --check-only .
```

**Configuration:** See `pyproject.toml` → `[tool.isort]`

### Flake8 (Linter)

**Check code:**
```bash
# Check all files
flake8 .

# Check specific file
flake8 main.py

# Show statistics
flake8 --statistics .
```

**Configuration:** See `.flake8`

### MyPy (Type Checker)

**Type checking:**
```bash
# Check all files
mypy .

# Check specific file
mypy main.py

# Ignore missing imports
mypy --ignore-missing-imports .
```

**Configuration:** See `mypy.ini`

---

## Adding New Features

### Adding New Supplier Extractor

1. **Create new extractor file:**
   ```bash
   touch extractors/supplier_name_extractor.py
   ```

2. **Implement extractor:**
   ```python
   # extractors/supplier_name_extractor.py
   from .base_extractor import BaseExtractor
   from .ls_extractor import InvoiceData
   
   class SupplierNameExtractor(BaseExtractor):
       def __init__(self):
           super().__init__()
           self.supplier_name = "SupplierName"
       
       def extract_from_pdf(self, pdf_path: str) -> Optional[InvoiceData]:
           # Implement extraction logic
           pass
   
   def extract_invoice_data(pdf_path: str):
       extractor = SupplierNameExtractor()
       return extractor.extract_from_pdf(pdf_path)
   ```

3. **Add tests:**
   ```python
   # tests/test_supplier_name_extraction.py
   def test_supplier_name_extraction():
       # Test implementation
       pass
   ```

4. **Update documentation:**
   - Add to README.md
   - Document extraction patterns
   - Add sample PDF to tests/samples/

### Adding New API Endpoint

1. **Define in main.py:**
   ```python
   @app.get("/new-endpoint")
   async def new_endpoint(api_key: str = Depends(verify_api_key)):
       """Endpoint description"""
       monitoring.metrics.increment_api_request()
       # Implementation
       return {"result": "data"}
   ```

2. **Add tests:**
   ```python
   def test_new_endpoint():
       from fastapi.testclient import TestClient
       from main import app
       
       client = TestClient(app)
       response = client.get("/new-endpoint", headers={"X-API-Key": "test-key"})
       assert response.status_code == 200
   ```

3. **Update documentation:**
   - API docs are auto-generated by FastAPI
   - Add to README.md if needed

---

## Debugging

### Using IPython

```python
# In code, add breakpoint
import ipdb; ipdb.set_trace()

# Run application, will pause at breakpoint
python main.py
```

**IPython debugger commands:**
- `n` - Next line
- `s` - Step into function
- `c` - Continue execution
- `l` - List code around current line
- `p variable` - Print variable
- `q` - Quit debugger

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Different log levels
logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
```

**View logs:**
```bash
# Tail log file
tail -f invoice_loader.log

# Search for errors
grep ERROR invoice_loader.log
```

### Visual Studio Code Debugging

**launch.json:**
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "main:app",
                "--reload"
            ],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

---

## Performance Profiling

### Using cProfile

```python
import cProfile
import pstats

# Profile a function
profiler = cProfile.Profile()
profiler.enable()

# Your code here
result = process_invoice(data)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 slowest
```

### Memory Profiling

```bash
# Install memory_profiler
pip install memory-profiler

# Decorate function
from memory_profiler import profile

@profile
def my_function():
    # Code to profile
    pass

# Run with profiler
python -m memory_profiler main.py
```

---

## Database Migrations

### Making Schema Changes

1. **Backup database:**
   ```bash
   cp invoices.db invoices.db.backup
   ```

2. **Write migration script:**
   ```python
   # migrations/add_column.py
   import sqlite3
   
   conn = sqlite3.connect('invoices.db')
   cursor = conn.cursor()
   
   cursor.execute("ALTER TABLE invoices ADD COLUMN new_column TEXT")
   conn.commit()
   conn.close()
   ```

3. **Test on dev database**

4. **Run on production with caution**

---

## Release Process

### Version Numbering

Follow Semantic Versioning (semver):
- `MAJOR.MINOR.PATCH` (e.g., 2.0.0)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Creating a Release

1. **Update version:**
   ```python
   # main.py
   version="2.1.0"
   
   # pyproject.toml
   version = "2.1.0"
   ```

2. **Update CHANGELOG.md:**
   ```markdown
   ## [2.1.0] - 2025-10-15
   
   ### Added
   - New feature X
   - New feature Y
   
   ### Fixed
   - Bug fix Z
   ```

3. **Create Git tag:**
   ```bash
   git tag -a v2.1.0 -m "Release version 2.1.0"
   git push origin v2.1.0
   ```

4. **Create GitHub Release:**
   - Go to Releases on GitHub
   - Create new release
   - Select tag v2.1.0
   - Add release notes
   - Attach deployment package if needed

---

## Resources

### Internal Documentation
- README.md - Project overview
- SECURITY.md - Security guidelines
- TROUBLESHOOTING.md - Common issues
- MONITORING.md - Monitoring setup

### External Resources
- FastAPI Docs: https://fastapi.tiangolo.com/
- Pydantic Docs: https://docs.pydantic.dev/
- pytest Docs: https://docs.pytest.org/
- Python Style Guide: https://pep8.org/

---

## Getting Help

1. Check documentation in this repository
2. Search existing GitHub issues
3. Ask in team chat/Slack
4. Contact: support@icc.sk

---

**Happy Coding! 🚀**