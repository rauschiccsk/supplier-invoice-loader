#!/usr/bin/env python3
"""
Generate FULL_PROJECT_CONTEXT.md - konsolidovaný context pre Claude.

Usage:
    python generate_full_context.py

Output:
    - FULL_PROJECT_CONTEXT.md (optimalizovaný pre jeden web_fetch)
"""

from pathlib import Path
from datetime import datetime


def get_latest_session_file():
    """Nájdi najnovší session note súbor."""
    sessions_dir = Path("docs/sessions")
    if not sessions_dir.exists():
        return None

    session_files = sorted(sessions_dir.glob("202*.md"), reverse=True)
    return session_files[0] if session_files else None


def read_file_safe(filepath):
    """Načítaj súbor bezpečne."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"[File not found: {filepath}]"
    except Exception as e:
        return f"[Error reading {filepath}: {e}]"


def estimate_tokens(text):
    """Hrubý odhad tokenov (1 token ≈ 4 znaky)."""
    return len(text) // 4


def generate_full_context():
    """Generuj konsolidovaný FULL_PROJECT_CONTEXT.md."""

    print("🚀 Generating FULL_PROJECT_CONTEXT.md...")

    sections = []
    total_tokens = 0

    # Header
    header = f"""# FULL PROJECT CONTEXT - Supplier Invoice Loader v2.0

**Automaticky generované:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Repository:** https://github.com/rauschiccsk/supplier_invoice_loader  
**Branch:** v2.0-multi-customer

---

> **Pre Claude:** Tento súbor obsahuje všetko potrebné na okamžitú prácu na projekte.
> Po načítaní odpovedz len: "✅ Projekt načítaný. Čo robíme?"

---

"""
    sections.append(("HEADER", header))

    # 1. MASTER_CONTEXT.md
    print("  📄 Loading MASTER_CONTEXT.md...")
    master_context = read_file_safe("docs/MASTER_CONTEXT.md")
    sections.append(("MASTER_CONTEXT", master_context))

    # 2. Latest session notes
    print("  📄 Loading latest session notes...")
    latest_session = get_latest_session_file()
    if latest_session:
        session_content = read_file_safe(latest_session)
        session_section = f"\n---\n\n# LATEST SESSION NOTES\n\n{session_content}\n"
        sections.append(("SESSION_NOTES", session_section))
    else:
        sections.append(("SESSION_NOTES", "\n---\n\n# LATEST SESSION NOTES\n\n[No session notes found]\n"))

    # 3. Project status summary
    print("  📄 Adding project status...")
    status = """
---

# QUICK PROJECT STATUS

## ✅ COMPLETE
- **STORY 1:** Python server production ready
- **Tests:** 80+ unit tests, 100% extraction rate
- **Services:** SupplierInvoiceLoader + CloudflaredMagerstav Windows Services
- **Tunnel:** magerstav-invoices.icc.sk deployed
- **Docs:** Complete documentation structure

## ⏳ IN PROGRESS
- Production deployment u MAGERSTAV (pripravené)

## 🔜 PLANNED
- **STORY 2:** Human-in-loop validácia (web UI)
- **STORY 3:** NEX Genesis API integrácia
- **STORY 4-6:** Advanced features

## 🎯 IMMEDIATE NEXT STEPS
1. Production deployment u MAGERSTAV
2. Real-world testing s L&Š faktúrami
3. Operator training
4. Monitoring prvého týždňa

---
"""
    sections.append(("STATUS", status))

    # 4. Key file locations
    print("  📄 Adding file structure...")
    file_structure = """
# KEY FILE LOCATIONS

## Configuration
- `config.py` - Hlavná konfigurácia
- `config_customer.py` - MAGERSTAV config (lokálne)
- `config_template.py` - Template pre nových zákazníkov

## Core Application
- `main.py` - FastAPI server
- `database.py` - SQLite wrapper
- `extractors/` - PDF extraction moduly
  - `ls_extractor.py` - L&Š špecifický extractor
  - `generic_extractor.py` - Generic fallback

## Documentation
- `docs/MASTER_CONTEXT.md` - Single source of truth
- `docs/sessions/` - Daily session notes
- `docs/architecture/` - Architektúra, n8n, cloudflared

## Deployment
- `service_installer.py` - Windows Service installer
- `INSTALL_CUSTOMER.md` - Deployment guide
- `DEPLOYMENT_CHECKLIST.md` - Deployment checklist

## Testing
- `tests/` - Unit tests
- `test_e2e.py` - End-to-end tests

---
"""
    sections.append(("FILES", file_structure))

    # 5. Quick reference commands
    print("  📄 Adding quick reference...")
    quick_ref = """
# QUICK REFERENCE

## Local Development
```bash
cd C:\\Development\\supplier_invoice_loader
.\\venv\\Scripts\\activate
python main.py
# Server: http://localhost:8000
```

## Testing
```bash
pytest tests/ -v
python test_e2e.py
```

## Windows Service
```bash
# Install
python service_installer.py

# Status
sc query SupplierInvoiceLoader

# Logs
type C:\\invoice-loader\\logs\\service.log
```

## Git Workflow
```bash
git status
git add .
git commit -m "feat: Your feature description"
git push origin v2.0-multi-customer
```

## Access Project Files
```
Base URL: https://raw.githubusercontent.com/rauschiccsk/supplier_invoice_loader/v2.0-multi-customer/

Manifest: project_file_access_manifest.json
Parts: project_file_access_*.json
```

---
"""
    sections.append(("QUICK_REF", quick_ref))

    # 6. Critical configurations
    print("  📄 Adding critical configurations...")
    configs = """
# CRITICAL CONFIGURATIONS

## MAGERSTAV Setup
- **Customer:** MÁGERSTAV, spol. s r.o.
- **IČO:** 31436871
- **Server:** Windows 11
- **PDF Storage:** `G:\\NEX\\IMPORT\\LS\\PDF`
- **XML Storage:** `G:\\NEX\\IMPORT\\LS\\XML`
- **Database:** `C:\\invoice-loader\\invoices.db`

## L&Š Supplier (Primary)
- **Name:** L&Š, s.r.o.
- **IČO:** 36555720
- **Email:** faktury@farby.sk
- **Extractor:** `ls_extractor.py`

## Cloudflared Tunnel
- **URL:** https://magerstav-invoices.icc.sk
- **Tunnel ID:** 0fdfffe9-b348-44b5-adcc-969681ac2786
- **Config:** C:\\cloudflared\\config.yml
- **Service:** CloudflaredMagerstav

## n8n Workflow
- **Server:** Central ICC server
- **Workflow:** Email → Extract PDF → POST to Python
- **Endpoint:** http://localhost:8000/invoice
- **Poll:** Every 1 minute

---
"""
    sections.append(("CONFIGS", configs))

    # Footer
    footer = """
---

# HOW TO USE THIS CONTEXT

## In New Chat
Just paste this URL:
```
https://raw.githubusercontent.com/rauschiccsk/supplier_invoice_loader/v2.0-multi-customer/FULL_PROJECT_CONTEXT.md
```

Claude will respond: "✅ Projekt načítaný. Čo robíme?"

## Update This File
Run locally:
```bash
python generate_full_context.py
git add FULL_PROJECT_CONTEXT.md
git commit -m "docs: Update FULL_PROJECT_CONTEXT"
git push origin v2.0-multi-customer
```

---

**END OF CONTEXT**
"""
    sections.append(("FOOTER", footer))

    # Combine all sections
    print("\n📊 Section sizes:")
    full_content = ""
    for name, content in sections:
        tokens = estimate_tokens(content)
        total_tokens += tokens
        print(f"   {name:20s}: {tokens:6d} tokens")
        full_content += content

    print(f"\n   {'TOTAL':20s}: {total_tokens:6d} tokens")

    # Token limit warning
    if total_tokens > 25000:  # Safe limit for web_fetch
        print("\n⚠️  WARNING: File is large! Consider reducing content.")
    else:
        print("\n✅ File size OK for web_fetch")

    # Save
    output_file = Path("FULL_PROJECT_CONTEXT.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_content)

    print(f"\n✅ Generated: {output_file}")
    print(f"   Size: {len(full_content):,} chars")
    print(f"   Tokens: ~{total_tokens:,}")

    print("\n📝 Next steps:")
    print("   1. git add FULL_PROJECT_CONTEXT.md")
    print("   2. git commit -m 'docs: Add consolidated project context'")
    print("   3. git push origin v2.0-multi-customer")
    print("   4. Test in new chat with URL:")
    print(
        "      https://raw.githubusercontent.com/rauschiccsk/supplier_invoice_loader/v2.0-multi-customer/FULL_PROJECT_CONTEXT.md")

    return output_file


if __name__ == "__main__":
    generate_full_context()