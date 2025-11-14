# Session Notes - Supplier Invoice Loader

**Project:** supplier-invoice-loader  
**Last Updated:** 2025-11-14  
**Status:** ✅ Development Environment Ready

---

## 🎯 Project Overview

Automatizované spracovanie dodávateľských faktúr cez email → n8n → Python FastAPI → NEX Genesis.

**Tech Stack:**
- Python 3.11+, FastAPI, SQLite, pdfplumber
- n8n workflows, Cloudflared tunnels
- Windows Service deployment

**Zákazníci:**
- MAGERSTAV, spol. s r.o. (production)
- ANDROS (planned)

**Dodávatelia:**
- L&Š, s.r.o. (IČO: 36555720)

---

## 📅 Session History

### Session 2025-11-14: Python Environment Setup & PyCharm Configuration

**Duration:** ~3 hours  
**Objective:** Setup development environment in PyCharm

#### ✅ Completed Tasks

1. **Python Virtual Environment**
   - Created `.venv` with Python 3.11.9
   - Installed production dependencies (fastapi, uvicorn, pdfplumber, etc.)
   - Installed development dependencies (pytest, black, isort, safety, etc.)
   - Fixed dependency conflicts (safety 2.3.5 → 3.2.0)

2. **Project Configuration**
   - Updated `pyproject.toml`:
     - Synchronized dependency versions with requirements.txt
     - Added `[tool.setuptools]` configuration for src/ package discovery
     - Fixed package metadata
   - Updated `requirements-dev.txt` (safety version)
   - Updated `.gitignore` (added *.egg-info, temp scripts)

3. **Import Fixes**
   - Fixed `src/utils/config.py` - import paths for config modules
   - Fixed `src/utils/monitoring.py` - removed duplicate imports, fixed database import
   - Fixed `src/utils/notifications.py` - removed duplicate imports, fixed database import
   - Fixed `tests/conftest.py` - removed triple duplicate imports
   - Fixed `tests/unit/test_import.py` - variable name error
   - Fixed `tests/unit/test_notifications.py` - deprecated pytest.config API

4. **Editable Install**
   - Installed project with `pip install -e .`
   - Enabled `from src.module import` syntax across project
   - Verified all imports working

5. **PyCharm Configuration**
   - Created run configurations:
     - FastAPI Server (main.py)
     - pytest - All Tests
     - pytest - Unit Tests
     - pytest - Integration Tests
   - Configured external tools:
     - Black (code formatter)
     - isort (import sorter)
   - Set Python interpreter to `.venv` (Python 3.11.9)

6. **Verification**
   - FastAPI server: ✅ Running on http://localhost:8000
   - API Docs: ✅ Accessible at http://localhost:8000/docs
   - Tests: 43 passed, 26 failed, 2 skipped (see issues below)
   - Imports: ✅ All project imports working

#### ⚠️ Known Issues

1. **Test Failures (26 failed)**
   - **API endpoint tests (16 failed):** Routes return 404 - endpoints may be missing in main.py
   - **Mock path errors (7 failed):** `@patch('notifications...')` should be `@patch('src.utils.notifications...')`
   - **XSS test (1 failed):** HTML escaping not implemented in email templates
   - **Config test (1 failed):** Environment variable override test
   - **Full invoice test (1 failed):** Missing sample PDF file
   
   **Decision:** Marked as technical debt, tests will be fixed in future session

2. **Temporary Helper Scripts**
   - Created during setup: `fix_conftest.py`, `fix_tests.py`, `fix_all_imports.py`
   - Not committed to Git (in .gitignore)
   - Generate new versions when needed

#### 📦 Files Changed

**Modified:**
- `pyproject.toml` - dependencies + setuptools config
- `requirements-dev.txt` - safety version
- `.gitignore` - new patterns
- `src/utils/config.py` - import fixes
- `src/utils/monitoring.py` - import fixes
- `src/utils/notifications.py` - import fixes
- `tests/conftest.py` - import fixes
- `tests/unit/test_import.py` - variable fix
- `tests/unit/test_notifications.py` - pytest API update

**Created:**
- `.venv/` - virtual environment
- `supplier_invoice_loader.egg-info/` - package metadata

#### 🎓 Lessons Learned

1. **Refactoring Impact:** Moving to src/ structure required fixing import paths across project
2. **Test Dependencies:** Mock paths need to match new module structure
3. **PyCharm Setup:** Proper interpreter and editable install crucial for imports
4. **Dependency Management:** pyproject.toml must sync with requirements.txt

#### 📋 Next Steps

1. **Fix Test Failures:**
   - Update mock paths in test_notifications.py
   - Check main.py for missing API endpoints
   - Add HTML escaping to email templates
   - Create sample PDF for tests

2. **Code Quality:**
   - Run Black on all Python files
   - Run isort on all imports
   - Optional: Add flake8 and mypy to external tools

3. **Documentation:**
   - Update developer guide with venv setup steps
   - Document PyCharm configuration

---

## ✅ Completed Work (Previous Sessions)

### STORY 1 - Production Ready (October 2025)
- Multi-customer SaaS architecture
- PDF extraction engine (pdfplumber)
- SQLite database v2 with multi-customer support
- Email notifications & alerting
- Windows Service support
- Cloudflared tunnel setup
- 80+ unit tests
- Complete documentation

### Project Refactoring (November 2025)

**Phase 1 - Project Structure:**
- Created new GitHub repository: supplier-invoice-loader
- Built professional src/ modular architecture
- Organized documentation into subdirectories
- Generated INIT_PROMPT_NEW_CHAT.md and unified docs

**Phase 2 - Code Migration:**
- Migrated 18 Python modules from root to src/
- Updated all imports to use src. prefix
- Moved scripts to scripts/
- Reorganized tests to tests/unit/
- Created minimal main.py entry point
- Clean root directory (6 files only)

**Phase 3 - Documentation:**
- Reorganized docs into guides/, operations/, deployment/
- Updated INIT_PROMPT with new structure
- Professional project organization

---

## 🗂️ Project Structure

```
supplier-invoice-loader/
├── .venv/                         # Virtual environment (Python 3.11.9)
├── src/                           # Python source code
│   ├── api/                      # FastAPI models
│   ├── business/                 # Business logic (ISDOC)
│   ├── database/                 # SQLite operations
│   ├── extractors/               # PDF extraction
│   └── utils/                    # Config, notifications, monitoring
├── docs/                          # Documentation
│   ├── INIT_PROMPT_NEW_CHAT.md  # Session initialization
│   ├── SESSION_NOTES.md         # This file
│   ├── guides/                   # Development guides
│   ├── operations/               # User & operations manuals
│   ├── deployment/               # Deployment guides
│   ├── architecture/             # Technical docs
│   └── database/                 # DB schemas
├── scripts/                       # Utility scripts
│   ├── service_installer.py     # Windows service installer
│   ├── generate_project_access.py  # Manifest generator
│   └── verify_installation.py   # Setup verification
├── config/                        # Configuration files
├── tests/                         # Test suite
├── deploy/                        # Deployment scripts
├── n8n-workflows/                # n8n workflow definitions
├── main.py                       # Application entry point
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── pyproject.toml               # Python project configuration
└── README.md
```

---

## 🔑 Critical Configuration

### MAGERSTAV
- IČO: 31436871
- PDF Storage: `G:\NEX\IMPORT\LS\PDF`
- XML Storage: `G:\NEX\IMPORT\LS\XML`
- Database: `C:\invoice-loader\invoices.db`

### L&Š Supplier
- IČO: 36555720
- Email: faktury@farby.sk
- Extractor: `src/extractors/ls_extractor.py`

### Cloudflared Tunnel
- URL: https://magerstav-invoices.icc.sk
- Tunnel ID: 0fdfffe9-b348-44b5-adcc-969681ac2786

---

## 🚀 Development Commands

### Setup
```bash
cd C:\Development\supplier-invoice-loader

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies (if needed)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install project in editable mode
pip install -e .
```

### Run Application
```bash
# With venv activated
python main.py

# Or in PyCharm: Run "Supplier Invoice Loader (FastAPI)" configuration

# Server: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Testing
```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# With coverage
pytest --cov=src --cov-report=html

# Or in PyCharm: Run "pytest - All Tests" configuration
```

### Code Formatting
```bash
# Format file with Black
black path/to/file.py

# Sort imports with isort
isort path/to/file.py

# Or in PyCharm: Right-click → External Tools → Black/isort
```

### Verification
```bash
# Verify installation
python scripts/verify_installation.py

# Test imports
python -c "from src.database import database; print('✅ OK')"
python -c "from src.extractors.ls_extractor import LSExtractor; print('✅ OK')"
```

---

## 📋 Architecture

### Data Flow
```
Gmail IMAP
  ↓
n8n Workflow (email monitoring)
  ↓
Python FastAPI Server (localhost:8000)
  ↓
PDF Extraction (pdfplumber)
  ↓
SQLite Database (invoices.db)
  ↓
XML Generation (ISDOC format)
  ↓
NEX Genesis API (customer ERP)
```

### Key Components

**src/extractors/ls_extractor.py:**
- L&Š specific PDF parser
- Extracts invoice data (number, date, amount, items)
- Handles multi-page invoices
- 100% success rate on 19 test invoices

**src/database/database.py:**
- SQLite wrapper with multi-customer support
- Duplicate detection (file hash)
- Status tracking (received, processed, error)
- NEX Genesis sync status

**src/business/isdoc_service.py:**
- ISDOC XML generation (Czech standard)
- Invoice data transformation
- XML validation

**src/utils/notifications.py:**
- Email alerts (errors, duplicates, daily summary)
- Gmail SMTP integration
- Template-based notifications

**src/utils/monitoring.py:**
- System health checks
- Disk space monitoring
- Process monitoring
- Heartbeat endpoint

---

## 🔧 Technical Details

### Python Environment
- **Version:** Python 3.11.9
- **Virtual Environment:** `.venv/` (not in Git)
- **Package Install:** Editable mode (`pip install -e .`)
- **IDE:** PyCharm Community Edition 2024.2.4

### Database Schema (SQLite)
- Table: invoices
- Key fields: file_hash (unique), invoice_number, customer_name
- Indexes: file_hash, invoice_number, status, customer_name
- Status values: received, processed, error, partial
- NEX sync: pending, synced, error

### Import Structure
All imports use `from src.module import`:
```python
from src.database import database
from src.api import models
from src.extractors.ls_extractor import LSExtractor
from src.business import isdoc_service
from src.utils import notifications, monitoring, config
```

### Configuration
- `config/config_customer.py` - customer-specific settings
- `config/config.template.yaml` - YAML config template
- `.env` - environment variables (not in Git)

---

## 💡 Best Practices

1. **Vždy aktivuj venv pred prácou:** `.\.venv\Scripts\Activate.ps1`
2. **Commit pred limitom chatu**
3. **Používaj INIT_PROMPT_NEW_CHAT.md pre nové chaty**
4. **Testuj na reálnych dátach pred deployment**
5. **Aktualizuj SESSION_NOTES.md po dokončení práce**
6. **Review code changes pred commit**
7. **Use src. prefix pre všetky importy**
8. **Regeneruj manifest po každom push:** `python scripts\generate_project_access.py`

---

## 🎯 Future Work

### Short-term (Next Session)
1. Fix 26 failing tests
2. Add missing API endpoints (if needed)
3. Implement HTML escaping in email templates
4. Run code formatting (Black + isort) on all files

### STORY 2 - Human-in-loop Validation
- Web interface for operators
- Approve/Reject workflow
- Invoice preview UI

### STORY 3-6 - Advanced Features
- NEX Genesis API direct integration
- OCR support for scanned PDFs
- Advanced monitoring dashboard
- Multi-supplier factory pattern

---

## 📞 Contact

**Developer:** rausch@icc.sk  
**Organization:** ICC Komárno  
**GitHub:** https://github.com/rauschiccsk/supplier-invoice-loader

---

**End of Session Notes**