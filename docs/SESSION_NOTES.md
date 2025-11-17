# Session Notes - Supplier Invoice Loader

**Project:** supplier-invoice-loader  
**Last Updated:** 2025-11-17  
**Status:** ✅ Test Fixes In Progress

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

### Session 2025-11-17: Notification Tests Fix

**Duration:** ~3 hours  
**Objective:** Fix failing notification tests and implement HTML escaping

#### ✅ Completed Tasks

1. **Mock Path Fixes**
   - Fixed 8 mock paths in test_notifications.py
   - Updated `@patch('notifications.X')` → `@patch('src.utils.notifications.X')`
   - Fixed `@patch('notifications.database.get_stats')` → `@patch('src.database.database.get_stats')`

2. **HTML Escaping Implementation (XSS Protection)**
   - Added `import html` to notifications.py
   - Implemented HTML escaping in email templates:
     - `_error_template()`: escaped_error_message, escaped_stack_trace
     - `_validation_failed_template()`: escaped_reason
   - Prevents XSS attacks through crafted error messages

3. **Variable Name Conflict Resolution**
   - Renamed local variable `html = f"""` → `html_content = f"""`
   - Resolved conflict with imported `html` module
   - Applied to all 3 template functions

4. **Authentication Test Fix**
   - Added `@patch` decorators for config.SMTP_USER and config.SMTP_PASSWORD
   - Test now properly mocks SMTP credentials
   - Authentication failure scenario now correctly returns False

5. **Test Results**
   - Before: 11 passed, 4 failed in test_notifications.py
   - After: 14 passed, 0 failed, 1 skipped
   - Coverage: 83% for notifications.py (improved from 77%)

#### 📦 Files Changed

**Modified:**
- `src/utils/notifications.py`
  - Added `import html`
  - Added HTML escaping in 3 template functions
  - Renamed local `html` variables to `html_content`
- `tests/unit/test_notifications.py`
  - Fixed 9 mock paths
  - Added 2 config patches for authentication test

**Temporary Scripts Created (deleted):**
- `fix_mock_paths.py`
- `rollback_and_fix.py`
- `fix_html_variable_conflict.py`
- `quick_fix_auth_test.py`

#### 🎓 Lessons Learned

1. **F-string Limitations:** Cannot call functions with backslash in f-string expressions - must escape values before f-string
2. **Variable Name Conflicts:** Local variables shadow module imports - be careful with common names like `html`, `json`, `os`
3. **Mock Paths:** After refactoring to src/ structure, all mock paths need updating
4. **Test Configuration:** Some tests need explicit config setup via mocks to test error conditions

#### 📊 Overall Test Status

**Current State:**
- **52 passed** (73% success rate)
- **17 failed** (24%)
- **2 skipped** (3%)

**Remaining Failures:**
- 16 API endpoint tests (404 errors - missing routes in main.py)
- 1 config test (environment variable override)

#### 📋 Next Steps

1. **Fix API Endpoint Tests (16 failed)**
   - Check main.py for missing routes
   - Add missing endpoints: /status, /metrics, /invoices, etc.
   - Verify API key authentication

2. **Fix Config Test (1 failed)**
   - test_config_environment_variable_override
   - Issue: Environment variable not being applied
   - Check env_loader.py logic

3. **Code Quality**
   - Run Black formatter on modified files
   - Run isort on imports
   - Update documentation

---

## ✅ Completed Work (Previous Sessions)

### Session 2025-11-14: Python Environment Setup & PyCharm Configuration

**Duration:** ~3 hours  
**Objective:** Setup development environment in PyCharm

**Achievements:**
- Created .venv with Python 3.11.9
- Installed all dependencies
- Fixed import paths for src/ structure
- Configured PyCharm (run configs, external tools)
- Fixed 26 duplicate imports and import errors
- Tests: 43 passed, 26 failed, 2 skipped

**Known Issues:**
- 26 test failures (API endpoints, mock paths, XSS test)
- Marked as technical debt

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

# Specific test file
pytest tests/unit/test_notifications.py -v

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
- HTML escaping for XSS protection

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
9. **Všetky fixe robíme cez .py scripty, nie .ps1**

---

## 🎯 Future Work

### Short-term (Next Session)
1. Fix 16 API endpoint tests (404 errors)
   - Check main.py for missing routes
   - Add /status, /metrics, /stats, /invoices endpoints
2. Fix 1 config test (environment override)
3. Run code formatting (Black + isort)

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