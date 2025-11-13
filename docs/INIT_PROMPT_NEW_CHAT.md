# Supplier Invoice Loader - Init Prompt

**Project:** supplier-invoice-loader (refactored structure)  
**Version:** 2.0  
**GitHub:** https://github.com/rauschiccsk/supplier_invoice_loader  
**Generated:** 2025-11-13 21:57

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
**Refactoring:** ✅ New src/ structure, unified docs

---

## 🗂️ Nová Štruktúra

```
supplier-invoice-loader/
├── docs/
│   ├── INIT_PROMPT_NEW_CHAT.md    # Tento súbor
│   ├── SESSION_NOTES.md           # Unified history
│   ├── architecture/              # Tech docs
│   └── database/                  # DB schemas & docs
│
├── src/                           # Python source code
│   ├── extractors/               # PDF extraction
│   ├── business/                 # Business logic
│   ├── database/                 # DB operations
│   ├── api/                      # FastAPI routes
│   └── utils/                    # Utilities
│
├── scripts/                       # Utility scripts
│   └── generate_project_access.py
│
├── config/                        # Configuration
│   └── config.yaml
│
├── database/
│   └── schemas/                  # SQL schemas
│
├── tests/                         # Test suite
│   ├── unit/
│   └── integration/
│
├── main.py                       # Entry point
└── supplier-invoice-loader_project_file_access.json
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
- **Extractor:** `ls_extractor.py`

### Cloudflared Tunnel
- **URL:** https://magerstav-invoices.icc.sk
- **Tunnel ID:** 0fdfffe9-b348-44b5-adcc-969681ac2786

---

## 🚀 Quick Commands

### Development
```bash
cd c:\Development\supplier-invoice-loader
.\venv\Scripts\activate
python main.py
# Server: http://localhost:8000
```

### Testing
```bash
pytest tests/ -v
python test_e2e.py
```

### Service Management
```bash
sc query SupplierInvoiceLoader
type C:\invoice-loader\logs\service.log
```

---

## 📋 Aktuálny Stav

### ✅ STORY 1 - DOKONČENÉ
- Multi-customer architecture
- PDF extraction engine (pdfplumber)
- SQLite database v2
- Email notifications
- Windows Service support
- Cloudflared tunnel
- 80+ unit tests
- Complete documentation

### 🔄 Refactoring Status
- ✅ Phase 1: Documentation structure
- 🚧 Phase 2: Code migration to src/
- ⏳ Phase 3: Testing & verification

### 📝 Planned (STORY 2-6)
- Human-in-loop validation (web UI)
- NEX Genesis API integration
- OCR support for scanned PDFs
- Advanced monitoring dashboard

---

## 📚 Dokumentácia

### Pre Operátorov
- [User Guide](../USER_GUIDE.md) - Slovak
- [Troubleshooting](../TROUBLESHOOTING.md)

### Pre Vývojárov
- [Development Guide](../DEVELOPMENT.md)
- [API Docs](http://localhost:8000/docs)
- [Testing Guide](../TESTING.md)
- [Session Notes](SESSION_NOTES.md) - Full history

### Architektúra
- [n8n Workflows](architecture/n8n-workflows.md)
- [Cloudflared Setup](architecture/cloudflared-setup.md)
- [Database Schema](database/TYPE_MAPPINGS.md)

---

## 🔗 Rýchly Prístup

**Manifest:** `supplier-invoice-loader_project_file_access.json`

**Core Modules:**
- `src/api/endpoints.py` - FastAPI routes
- `src/database/database.py` - SQLite operations
- `src/extractors/ls_extractor.py` - L&Š PDF extractor
- `src/business/invoice_service.py` - Business logic

**Configuration:**
- `config/config.yaml` - Main config
- `config/config.template.yaml` - Template

---

## 💡 Best Practices

1. **Vždy commit pred limitom chatu**
2. **Session notes po každom pracovnom dni**
3. **Testuj na reálnych dátach**
4. **Používaj INIT_PROMPT ako single source of truth**
5. **Review code changes pred commit**

---

## 📞 Kontakt

**Developer:** rausch@icc.sk  
**Support:** support@icc.sk  
**GitHub:** @rauschiccsk

---

## 📖 Kontext z MASTER_CONTEXT

\# 🎯 MASTER CONTEXT - Supplier Invoice Loader Project



\*\*Single Source of Truth pre celý projekt\*\*



---



\## 📊 Project Overview



\### Základné informácie

\- \*\*Projekt:\*\* Supplier Invoice Loader v2.0

\- \*\*Účel:\*\* Automatizované spracovanie dodávateľských faktúr cez email → n8n → Python → NEX Genesis

\- \*\*Status:\*\* STORY 1 Complete - Production Ready

\- \*\*Vývojár:\*\* ICC (rausch@icc.sk)

\- \*\*Lokalizácia:\*\* Komárno, SK



\### GitHub Repository

```

URL: https://github.com/rauschiccsk/supplier\_invoice\_loader

Branch: v2.0-multi-customer

Lokálna cesta: c:\\Development\\supplier\_invoice\_loader

```



\### Kľúčoví zákazníci

1\. \*\*MAGERSTAV, spol. s r.o.\*\* (Primárny zákazník)

&nbsp;  - Dodávateľ: L\&Š, s.r.o. (farby, laky)

&nbsp;  - Windows 11 deployment

&nbsp;  - NEX Genesis integrácia



2\. \*\*ANDROS\*\* (Plánovaný)

&nbsp;  - Windows Server 2012 R2

&nbsp;  - Cloudflared tunnel



---



\## 🏗️ Architektúra systému



\### High-Level Diagram

```

┌─────────────────────────────────────────────────────────────┐

│                    CENTRÁLNY ICC SERVER                      │

│                  (128GB RAM, 12 cores)                       │

│                                                              │

│  ┌──────────────────────────────────────────────────────┐  │

│  │  n8n Workflows Engine                                 │  │

│  │  - Email IMAP monitoring                              │  │

│  │  - PDF attachment processing                          │  │

│  │  - Multi-customer workflow management                 │  │

│  └──────────────────────────────────────────────────────┘  │

│                          ↓                                   │

│  ┌──────────────────────────────────────────────────────┐  │

│  │  Python FastAPI Servers (per zákazník)               │  │

│  │  - Invoice processing                                 │  │

│  │  - PDF extraction (pdfplumber)                        │  │

│  │  - Data validation                                    │  │

│  │  - SQLite database                                    │  │

│  └──────────────────────────────────────────────────────┘  │

└─────────────────────────────────────────────────────────────┘

&nbsp;                         ↓

&nbsp;                  (Cloudflare Tunnel)

&nbsp;                         ↓

┌──────────────────────────────────────────────────────────────┐

│                    ZÁKAZNÍCKE SERVERY                         │

│  ┌────────────────────┐       ┌─────────────────────────┐   │

│  │  Windows 11        │       │ Windows Server 2012 R2   │   │

│  │  (MAGERSTAV)       │       │ (budúci zákazník)        │   │

│  ├────────────────────┤       ├─────────────────────────┤   │

│  │ Python Server:8000 │       │ Python Server:8000       │   │

│  │ Windows Service    │       │ Windows Service          │   │

│  │ SQLite DB          │       │ SQLite DB                │   │

│  │ PDF/XML Storage    │       │ PDF/XML Storage          │   │

│  └────────────────────┘       └─────────────────────────┘   │

│           ↓                              ↓                    │

│  ┌────────────────────┐       ┌─────────────────────────┐   │

│  │ NEX Genesis        │       │ NEX Genesis              │   │

│  │ (Delphi/Pervasive) │       │ (Delphi/Pervasive)       │   │

│  │ Port: 8080/API     │       │ Port: 8080/API           │   │

│  └────────────────────┘       └─────────────────────────┘   │

└──────────────────────────────────────────────────────────────┘

```



\### Tech Stack



\*\*Backend:\*\*

\- Python 3.10+

\- FastAPI framework

\- pdfplumber (PDF extraction)

\- SQLite (database)

\- Windows Service (NSSM wrapper)



\*\*Automatizácia:\*\*

\- n8n workflows

\- Email IMAP trigger

\- Cloudflared tunnels (secure connection)



\*\*Deployment:\*\*

\- Windows 11 (development \& MAGERSTAV)

\- Windows Server 2012 R2 (plánované)

\- Git-based deployment



\*\*External Systems:\*\*

\- NEX Genesis (Delphi informačný systém)

\- Pervasive database

\- Gmail SMTP (notifikácie)



---



\## 📁 Projektová štruktúra



```

supplier\_invoice\_loader/

├── docs/                          # Dokumentácia

│   ├── MASTER\_CONTEXT.md         # Tento súbor - Single Source of Truth

│   ├── architecture/             # Architektonické diagramy a popisy

│   │   ├── n8n-workflows.md

│   │   ├── cloudflared-setup.md

│   │   └── python-api.md

│   ├── decisions/                # Architecture Decision Records (ADR)

│   │   └── ADR-001-example.md

│   ├── sessions/                 # Daily/session notes

│   │   └── 2025-10-17-session.md

│   └── troubleshooting/          # Známe problémy a riešenia

│       └── common-issues.md

├── src/                          # Python source code

│   ├── main.py                   # FastAPI aplikácia

│   ├── database.py               # SQLite wrapper

│   ├── extractors/               # PDF extraction moduly

│   │   ├── \_\_init\_\_.py

│   │   ├── generic\

---

## 📅 Latest Session Summary

# Session Notes
Daily work logs and session summaries.


---

**Pre kompletný session history pozri:** [SESSION_NOTES.md](SESSION_NOTES.md)

**End of Init Prompt**
