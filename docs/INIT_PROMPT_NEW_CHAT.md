# Supplier Invoice Loader - Init Prompt

**Project:** supplier-invoice-loader (refactored structure)  
**Version:** 2.0  
**GitHub:** https://github.com/rauschiccsk/supplier-invoice-loader  
**Generated:** 2025-11-14

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
**Flow:** Email → n8n → Python FastAPI → NEX Genesis  
**Stack:** Python 3.10+, FastAPI, SQLite, n8n, Cloudflared

**Status:** Production Ready (STORY 1 Complete)  
**Refactoring:** ✅ Phase 1 & 2 Complete - Professional src/ structure

---

## 🗂️ Projektová Štruktúra

```
supplier-invoice-loader/
├── src/                           # Python source code (modular)
│   ├── api/                      # FastAPI models
│   │   ├── __init__.py
│   │   └── models.py
│   ├── business/                 # Business logic
│   │   ├── __init__.py
│   │   └── isdoc_service.py
│   ├── database/                 # DB operations
│   │   ├── __init__.py
│   │   └── database.py
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
│       └── monitoring.py
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
│   ├── generate_project_access.py
│   ├── service_installer.py
│   └── cleanup_*.py
│
├── config/                        # Configuration
│   ├── config_customer.py
│   ├── config_template.py
│   ├── config.template.yaml
│   └── .env.example
│
├── database/
│   └── schemas/                  # SQL schemas
│       └── README.md
│
├── tests/                         # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── samples/                  # Test data
│   └── conftest.py
│
├── deploy/                        # Deployment scripts
│   ├── build_package.py
│   ├── deploy.bat
│   └── test-deployment.ps1
│
├── n8n-workflows/                 # n8n workflow definitions
│   ├── n8n-SupplierInvoiceEmailLoader.json
│   └── template.json
│
├── main.py                       # Application entry point
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── pyproject.toml               # Python project configuration
├── .gitignore
└── README.md
```

---

## 🔑 Kritická Konfigurácia

### MAGERSTAV Setup
- **IČO:** 31436871
- **PDF Storage:** `G:\NEX\IMPORT\LS\PDF`
- **XML Storage:** `G:\NEX\IMPORT\LS\XML`
- **Database:** `C:\invoice-loader\invoices.db`

### L&Š Dodávateľ
- **IČO:** 36555720
- **Email:** faktury@farby.sk
- **Extractor:** `src/extractors/ls_extractor.py`

### Cloudflared Tunnel
- **URL:** https://magerstav-invoices.icc.sk
- **Tunnel ID:** 0fdfffe9-b348-44b5-adcc-969681ac2786

---

## 🚀 Quick Commands

### Development
```bash
cd C:\Development\supplier-invoice-loader
.\venv\Scripts\activate
python main.py
# Server: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Testing
```bash
pytest tests/ -v
pytest tests/unit/ -v
pytest --cov=src --cov-report=html
```

### Import Testing
```bash
python -c "from src.database import database; print('✅ OK')"
python -c "from src.extractors.ls_extractor import LSExtractor; print('✅ OK')"
```

---

## 📋 Aktuálny Stav

### ✅ Refactoring Complete (2025-11-14)
- ✅ Phase 1: Project structure & documentation
- ✅ Phase 2: Code migration to src/
- ✅ New GitHub repository: supplier-invoice-loader
- ✅ Professional modular architecture
- ✅ Organized documentation (guides/, operations/, deployment/)
- ✅ All imports updated to src. prefix

### ✅ STORY 1 - DOKONČENÉ
- Multi-customer architecture
- PDF extraction engine (pdfplumber)
- SQLite database v2
- Email notifications
- Windows Service support
- Cloudflared tunnel
- 80+ unit tests
- Complete documentation

### 📝 Planned (STORY 2-6)
- Human-in-loop validation (web UI)
- NEX Genesis API integration
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
- `src/api/models.py` - Pydantic models
- `src/database/database.py` - Database operations
- `src/extractors/ls_extractor.py` - L&Š PDF extractor
- `src/business/isdoc_service.py` - ISDOC XML generation
- `src/utils/notifications.py` - Email notifications
- `src/utils/monitoring.py` - System monitoring

**Configuration:**
- `config/config.template.yaml` - Config template
- `config/config_customer.py` - Customer config

**Scripts:**
- `scripts/service_installer.py` - Windows service installer
- `scripts/generate_project_access.py` - Manifest generator

---

## 💡 Best Practices

1. **Vždy commit pred limitom chatu**
2. **Session notes po každom pracovnom dni**
3. **Testuj na reálnych dátach**
4. **Používaj INIT_PROMPT ako single source of truth**
5. **Review code changes pred commit**
6. **Aktualizuj importy: použiť `from src.module import`**

---

## 📞 Kontakt

**Developer:** rausch@icc.sk  
**Support:** support@icc.sk  
**GitHub:** @rauschiccsk  
**Organization:** ICC Komárno (Innovation & Consulting Center)

---

## 🏗️ Architektúra

### High-Level Flow
```
Email (Gmail) 
  → n8n Workflow (IMAP trigger)
    → Python FastAPI Server (invoice processing)
      → PDF Extraction (pdfplumber)
        → SQLite Database
          → XML Generation (ISDOC)
            → NEX Genesis API (customer ERP)
```

### Tech Stack
- **Backend:** Python 3.10+, FastAPI, Uvicorn
- **PDF Processing:** pdfplumber, PyPDF2
- **Database:** SQLite 3.x
- **Automation:** n8n workflows
- **Tunneling:** Cloudflared
- **Service:** Windows Service (NSSM wrapper)
- **Notifications:** Gmail SMTP

---

## 📖 Projekt Info

**Zákazníci:**
- MAGERSTAV, spol. s r.o. (production)
- ANDROS (planned)

**Dodávatelia:**
- L&Š, s.r.o. (IČO: 36555720) - farby, laky

**Environment:**
- Windows 11 / Windows Server 2012 R2
- Python 3.10+
- Local SQLite database
- Network file storage (PDF/XML)

---

**Pre kompletný development history pozri:** [SESSION_NOTES.md](SESSION_NOTES.md)

**End of Init Prompt**