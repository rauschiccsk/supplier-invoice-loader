# Supplier Invoice Loader - Init Prompt

**Project:** supplier-invoice-loader (refactored structure)  
**Version:** 2.0  
**GitHub:** https://github.com/rauschiccsk/supplier-invoice-loader  
**Last Updated:** 2025-11-17

---

## 🎯 Quick Start

Pre nový chat načítaj tento URL:
```
https://raw.githubusercontent.com/rauschiccsk/supplier-invoice-loader/main/docs/INIT_PROMPT_NEW_CHAT.md
```

Claude odpovie: **"✅ Projekt načítaný. Čo robíme?"**

---

## 📊 Project Overview

**Účel:** Automatizované spracovanie dodávateľských faktúr  
**Flow:** Email → n8n → Python FastAPI → PostgreSQL Staging → invoice-editor → NEX Genesis  
**Stack:** Python 3.11+, FastAPI, SQLite, PostgreSQL, n8n, Cloudflared

**Status:** Development - PostgreSQL Integration Complete ✅  
**Production:** STORY 1 Complete + invoice-editor Integration  
**Refactoring:** ✅ Phase 1 & 2 Complete - Professional src/ structure

---

## 🔄 Integration Points

### invoice-editor Integration (NEW - 2025-11-17)
- **Purpose:** Operator approval workflow before NEX Genesis import
- **Database:** PostgreSQL (invoice_staging)
- **Tables:** invoices_pending, invoice_items_pending
- **Workflow:** supplier-invoice-loader → PostgreSQL → invoice-editor GUI → NEX Genesis
- **Status:** Integrated ✅

**Components:**
- `src/database/postgres_staging.py` - PostgreSQL client (pg8000)
- `src/utils/text_utils.py` - Data sanitization utilities
- `config.POSTGRES_STAGING_ENABLED` - Enable/disable flag

**Environment:**
```powershell
$env:POSTGRES_PASSWORD = "your-password"
```

**Schema:**
- **invoices_pending:** Invoice headers (status: pending → approved → imported)
- **invoice_items_pending:** Invoice line items (editable by operator)

---

## 🗂️ Projektová Štruktúra

```
supplier-invoice-loader/
├── .venv/                         # Virtual environment (Python 3.11.9)
├── src/                           # Python source code (modular)
│   ├── api/                      # FastAPI models
│   │   ├── __init__.py
│   │   └── models.py
│   ├── business/                 # Business logic
│   │   ├── __init__.py
│   │   └── isdoc_service.py
│   ├── database/                 # DB operations
│   │   ├── __init__.py
│   │   ├── database.py          # SQLite operations
│   │   └── postgres_staging.py  # PostgreSQL staging (NEW)
│   ├── extractors/               # PDF extraction
│   │   ├── __init__.py
│   │   ├── base_extractor.py
│   │   ├── generic_extractor.py
│   │   └── ls_extractor.py
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── config.py
│       ├── env_loader.py
│       ├── notifications.py
│       ├── monitoring.py
│       └── text_utils.py        # String sanitization (NEW)
│
├── docs/                          # Documentation
│   ├── INIT_PROMPT_NEW_CHAT.md   # This file
│   ├── SESSION_NOTES.md          # Development history
│   ├── architecture/             # Architecture docs
│   ├── database/                 # DB schemas & docs
│   ├── deployment/               # Deployment guides
│   ├── operations/               # Operations manuals
│   └── guides/                   # Development guides
│
├── scripts/                       # Utility scripts
│   ├── generate_project_access.py  # Manifest generator
│   ├── service_installer.py        # Windows service installer
│   └── verify_installation.py      # Setup verification
│
├── config/                        # Configuration
│   ├── config_customer.py
│   ├── config_template.py        # PostgreSQL config added
│   ├── config.template.yaml
│   └── .env.example
│
├── tests/                         # Test suite (69 passing ✅)
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── samples/                  # Test data
│   └── conftest.py
│
├── deploy/                        # Deployment scripts
├── n8n-workflows/                 # n8n workflow definitions
├── main.py                       # Application entry point (complete workflow)
├── requirements.txt              # Production dependencies (includes pg8000)
├── requirements-dev.txt          # Development dependencies
├── pyproject.toml               # Python project configuration
├── .gitignore
└── README.md
```

---

## 🔑 Kritická Konfigurácia

### Development Environment
- **Python:** 3.11.9 (in `.venv/`)
- **IDE:** PyCharm Community Edition 2024.2.4
- **Install Mode:** Editable (`pip install -e .`)
- **Package:** `supplier-invoice-loader==2.0.0`

### MAGERSTAV Setup
- **IČO:** 31436871
- **PDF Storage:** `G:\NEX\IMPORT\LS\PDF`
- **XML Storage:** `G:\NEX\IMPORT\LS\XML`
- **Database:** `C:\invoice-loader\invoices.db`

### L&Š Dodávateľ
- **IČO:** 36555720
- **Email:** faktury@farby.sk
- **Extractor:** `src/extractors/ls_extractor.py`

### PostgreSQL Staging (invoice-editor integration) - NEW
- **Enabled:** True/False (POSTGRES_STAGING_ENABLED)
- **Host:** localhost (default)
- **Port:** 5432
- **Database:** invoice_staging
- **User:** invoice_user
- **Password:** ENV variable (POSTGRES_PASSWORD)

### Cloudflared Tunnel
- **URL:** https://magerstav-invoices.icc.sk
- **Tunnel ID:** 0fdfffe9-b348-44b5-adcc-969681ac2786

---

## 🚀 Quick Commands

### Development Setup
```powershell
cd C:\Development\supplier-invoice-loader

# Activate virtual environment (ALWAYS FIRST!)
.\.venv\Scripts\Activate.ps1

# Install dependencies (if needed)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install PostgreSQL driver (NEW)
pip install pg8000

# Install project in editable mode
pip install -e .

# Set PostgreSQL password (if using invoice-editor integration)
$env:POSTGRES_PASSWORD = "your-postgres-password"
```

### Run Application
```powershell
# Activate venv first!
.\.venv\Scripts\Activate.ps1

# Start server
python main.py

# Server: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### PyCharm
```
Run Configurations:
  - "Supplier Invoice Loader (FastAPI)" - Start server
  - "pytest - All Tests" - Run all tests
  - "pytest - Unit Tests" - Run unit tests only

External Tools:
  - Black - Format File (code formatter)
  - isort - Sort Imports (import organizer)
```

### Testing
```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Specific test file
pytest tests/unit/test_api.py -v

# With coverage
pytest --cov=src --cov-report=html

# Current status: 69 passed, 0 failed, 2 skipped ✅
```

### Import Testing
```powershell
python -c "from src.database import database; print('✅ OK')"
python -c "from src.extractors.ls_extractor import LSExtractor; print('✅ OK')"
python -c "from src.database.postgres_staging import PostgresStagingClient; print('✅ OK')"
python -c "from src.utils.text_utils import clean_string; print('✅ OK')"
```

### Verification
```powershell
# Verify complete installation
python scripts/verify_installation.py
```

---

## 📋 Aktuálny Stav

### ✅ PostgreSQL Staging Integration (2025-11-17)
- ✅ PostgreSQL client implemented (pg8000)
- ✅ String sanitization utilities (text_utils.py)
- ✅ Config extended with PostgreSQL settings
- ✅ POST /invoice endpoint - full workflow implemented
- ✅ Automatic insert to invoice-editor staging database
- ✅ Duplicate detection in PostgreSQL
- ✅ Optional integration (can be disabled)
- ✅ Error handling (PostgreSQL errors don't fail process)
- ✅ Detailed logging and response metadata

### ✅ Complete API Implementation (2025-11-17)
- ✅ All 8 API endpoints implemented
- ✅ FastAPI request tracking middleware
- ✅ API key authentication (X-API-Key header)
- ✅ Health checks and monitoring endpoints
- ✅ Prometheus metrics support
- ✅ Error handling in all endpoints

### ✅ All Tests Passing (2025-11-17)
- ✅ 69 unit tests passing (100% success rate)
- ✅ 2 tests skipped (integration tests)
- ✅ 0 failing tests
- ✅ Coverage: ~80% overall
- ✅ API endpoint tests: 16/16 passing
- ✅ Config tests: 14/14 passing
- ✅ Monitoring tests: 20/20 passing
- ✅ Notification tests: 14/14 passing

### ✅ Development Environment Setup (2025-11-14)
- ✅ Python 3.11.9 virtual environment (`.venv/`)
- ✅ All dependencies installed (production + dev)
- ✅ Project installed in editable mode (`pip install -e .`)
- ✅ PyCharm configured (run configs, external tools)
- ✅ FastAPI server running (http://localhost:8000)
- ✅ Import fixes completed (src/utils/, tests/)

### ✅ Refactoring Complete (2025-11-14)
- ✅ Phase 1: Project structure & documentation
- ✅ Phase 2: Code migration to src/
- ✅ New GitHub repository: supplier-invoice-loader
- ✅ Professional modular architecture
- ✅ Organized documentation (guides/, operations/, deployment/)
- ✅ All imports updated to src. prefix

### ✅ STORY 1 - Production Ready
- Multi-customer architecture
- PDF extraction engine (pdfplumber)
- SQLite database v2
- Email notifications
- Windows Service support
- Cloudflared tunnel
- 69 unit tests (all passing)
- Complete documentation

### 📝 Planned (STORY 2-6)
- Human-in-loop validation (invoice-editor GUI) ✅ INTEGRATED
- NEX Genesis API direct integration (via invoice-editor)
- OCR support for scanned PDFs
- Advanced monitoring dashboard

---

## 📚 Dokumentácia

### Pre Operátorov
- [User Guide](operations/USER_GUIDE.md)
- [Troubleshooting](operations/TROUBLESHOOTING.md)
- [Monitoring](operations/MONITORING.md)
- [Email Alerting](operations/EMAIL_ALERTING.md)

### Pre Vývojárov
- [Development Guide](guides/DEVELOPMENT.md)
- [Testing Guide](guides/TESTING.md)
- [Python Setup](guides/PYTHON_SETUP.md)
- [Security](guides/SECURITY.md)
- [N8N Setup](guides/N8N_WORKFLOW_SETUP.md)
- [Session Notes](SESSION_NOTES.md)

### Deployment
- [Deployment Checklist](deployment/DEPLOYMENT_CHECKLIST.md)
- [Install Customer](deployment/INSTALL_CUSTOMER.md)
- [Windows Service Guide](deployment/WINDOWS_SERVICE_GUIDE.md)
- [Release Notes](deployment/RELEASE_NOTES_v2.0.0.md)

### Architektúra
- [Database Schema](database/TYPE_MAPPINGS.md)
- [Architecture Decisions](decisions/)

---

## 🔗 Rýchly Prístup

**Core Modules:**
- `main.py` - FastAPI application (complete workflow with PostgreSQL)
- `src/api/models.py` - Pydantic models
- `src/database/database.py` - SQLite operations
- `src/database/postgres_staging.py` - PostgreSQL staging client (NEW)
- `src/extractors/ls_extractor.py` - L&Š PDF extractor
- `src/business/isdoc_service.py` - ISDOC XML generation
- `src/utils/text_utils.py` - String sanitization (NEW)
- `src/utils/notifications.py` - Email notifications (83% coverage)
- `src/utils/monitoring.py` - System monitoring & metrics

**Configuration:**
- `config/config.template.yaml` - Config template
- `config/config_customer.py` - Customer config
- `config/config_template.py` - PostgreSQL config added

**Scripts:**
- `scripts/service_installer.py` - Windows service installer
- `scripts/generate_project_access.py` - Manifest generator
- `scripts/verify_installation.py` - Installation verification

**Testing:**
- `tests/unit/` - Unit tests (69 passing)
- `tests/conftest.py` - Pytest configuration & fixtures

---

## 💡 Best Practices

1. **VŽDY aktivuj venv pred prácou:** `.\.venv\Scripts\Activate.ps1`
2. **Commit pred limitom chatu**
3. **Session notes po každom pracovnom dni**
4. **Testuj na reálnych dátach**
5. **Používaj INIT_PROMPT ako single source of truth**
6. **Review code changes pred commit**
7. **Aktualizuj importy: používaj `from src.module import`**
8. **Regeneruj manifest po každom push:** `python scripts\generate_project_access.py`
9. **Všetky fixe cez .py scripty, nie .ps1**
10. **Run tests before commit:** `pytest tests/unit/ -v`
11. **PostgreSQL heslo vždy cez ENV:** `$env:POSTGRES_PASSWORD = "..."`
12. **Test PostgreSQL connection pred produkciou**
13. **PostgreSQL je optional:** Môže byť vypnutý (POSTGRES_STAGING_ENABLED=False)
14. **Clean strings pre PostgreSQL:** Používaj text_utils.clean_string()

---

## 📞 Kontakt

**Developer:** rausch@icc.sk  
**Support:** support@icc.sk  
**GitHub:** @rauschiccsk  
**Organization:** ICC Komárno (Innovation & Consulting Center)

---

## 🗝️ Architektúra

### High-Level Flow
```
Email (Gmail) 
  ↓ n8n Workflow (IMAP trigger)
    ↓ Python FastAPI Server (invoice processing)
      ↓ PDF Extraction (pdfplumber)
        ├─→ SQLite Database (metadata)
        ├─→ XML Generation (ISDOC)
        ├─→ File Storage (PDF/XML)
        └─→ PostgreSQL Staging (NEW - invoice-editor)
              ↓
            GUI Approval (invoice-editor)
              ↓
            NEX Genesis API (customer ERP)
```

### Tech Stack
- **Backend:** Python 3.11+, FastAPI, Uvicorn
- **PDF Processing:** pdfplumber, PyPDF2
- **Database:** SQLite 3.x, PostgreSQL (staging)
- **PostgreSQL Driver:** pg8000 (Pure Python, 32-bit compatible)
- **Automation:** n8n workflows
- **Tunneling:** Cloudflared
- **Service:** Windows Service (NSSM wrapper)
- **Notifications:** Gmail SMTP
- **Development:** PyCharm, pytest, Black, isort

---

## 📖 Projekt Info

**Zákazníci:**
- MAGERSTAV, spol. s r.o. (production)
- ANDROS (planned)

**Dodávatelia:**
- L&Š, s.r.o. (IČO: 36555720) - farby, laky

**Integration:**
- invoice-editor (GUI approval workflow) ✅

**Environment:**
- Development: Windows 11, Python 3.11.9, PyCharm
- Production: Windows Server 2012 R2, Python 3.10+
- Local SQLite database
- PostgreSQL staging database (invoice-editor)
- Network file storage (PDF/XML)

---

## 📝 Dependencies

**Production (requirements.txt):**
```
fastapi>=0.104.0
uvicorn>=0.24.0
pdfplumber>=0.10.0
python-multipart>=0.0.6
pyyaml>=6.0
python-dateutil>=2.8.2
pg8000>=1.29.0              # PostgreSQL driver (NEW)
```

**Development (requirements-dev.txt):**
```
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.10.0
isort>=5.12.0
mypy>=1.6.0
```

---

**Pre kompletnú development history pozri:** [SESSION_NOTES.md](SESSION_NOTES.md)

**End of Init Prompt**