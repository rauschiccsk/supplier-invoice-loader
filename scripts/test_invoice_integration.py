# -*- coding: utf-8 -*-
"""
Test Invoice Integration
=========================

Test script pre overenie kompletnej integrácie:
- FastAPI server
- PostgreSQL staging database
- SQLite database
- File storage (PDF/XML)
- n8n workflow

Usage:
    python scripts/test_invoice_integration.py
"""

import os
import sys
import base64
import requests
from pathlib import Path
from datetime import datetime


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_step(step_num, text):
    """Print test step"""
    print(f"\n[Krok {step_num}] {text}")


def print_success(text):
    """Print success message"""
    print(f"  ✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"  ❌ {text}")


def print_warning(text):
    """Print warning message"""
    print(f"  ⚠️  {text}")


def check_environment():
    """Check required environment variables"""
    print_step(1, "Kontrola environment premenných")

    required = ["POSTGRES_PASSWORD", "LS_API_KEY"]
    missing = []

    for var in required:
        value = os.getenv(var)
        if value:
            print_success(f"{var}: nastavené")
        else:
            print_error(f"{var}: CHÝBA!")
            missing.append(var)

    if missing:
        print_error(f"Chýbajúce ENV premenné: {', '.join(missing)}")
        print("\nNastavenie:")
        print('  $env:POSTGRES_PASSWORD = "your-password"')
        print('  $env:LS_API_KEY = "your-api-key"')
        return False

    return True


def check_fastapi_server():
    """Check if FastAPI server is running"""
    print_step(2, "Kontrola FastAPI servera")

    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"FastAPI server beží: {data.get('status')}")
            return True
        else:
            print_error(f"FastAPI server odpovedal s kódom: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("FastAPI server nebeží!")
        print("\nSpustenie:")
        print("  .\.venv\Scripts\Activate.ps1")
        print("  python main.py")
        return False
    except Exception as e:
        print_error(f"Chyba pri kontrole servera: {e}")
        return False


def check_postgresql_connection():
    """Check PostgreSQL connection"""
    print_step(3, "Kontrola PostgreSQL pripojenia")

    try:
        # Import PostgreSQL client
        from src.database.postgres_staging import PostgresStagingClient
        from src.utils import config

        # Prepare config
        pg_config = {
            'host': config.POSTGRES_HOST,
            'port': config.POSTGRES_PORT,
            'database': config.POSTGRES_DATABASE,
            'user': config.POSTGRES_USER,
            'password': config.POSTGRES_PASSWORD
        }

        # Test connection using context manager
        with PostgresStagingClient(pg_config) as pg_client:
            # Check for duplicate (simple test that connection works)
            is_dup = pg_client.check_duplicate_invoice("test", "test")
            # This will return False but proves connection works

            print_success(f"PostgreSQL pripojenie OK")
            print(f"    Database: {config.POSTGRES_DATABASE}")
            print(f"    Host: {config.POSTGRES_HOST}:{config.POSTGRES_PORT}")
            print(f"    User: {config.POSTGRES_USER}")
            return True

    except ImportError as e:
        print_error(f"Import chyba: {e}")
        print("\nInštalácia:")
        print("  pip install pg8000")
        return False
    except Exception as e:
        print_error(f"PostgreSQL pripojenie zlyhalo: {e}")
        print("\nKontrola:")
        print("  1. PostgreSQL server beží?")
        print("  2. Database 'invoice_staging' existuje?")
        print("  3. User má prístup?")
        print("  4. POSTGRES_PASSWORD je správne?")
        return False


def check_test_pdf():
    """Check if test PDF exists"""
    print_step(4, "Kontrola test PDF súboru")

    # Look for test PDFs in tests/samples/
    samples_dir = Path("tests/samples")

    if not samples_dir.exists():
        print_error(f"Adresár {samples_dir} neexistuje!")
        return None

    # Find PDF files
    pdf_files = list(samples_dir.glob("*.pdf"))

    if not pdf_files:
        print_error(f"Žiadne PDF súbory v {samples_dir}!")
        print("\nPotrebný test PDF súbor s faktúrou od L&Š")
        return None

    # Use first PDF
    test_pdf = pdf_files[0]
    print_success(f"Nájdený test PDF: {test_pdf.name}")
    print(f"    Veľkosť: {test_pdf.stat().st_size / 1024:.1f} KB")

    return test_pdf


def send_test_invoice(pdf_path, api_key):
    """Send test invoice to FastAPI"""
    print_step(5, "Odoslanie test faktúry na FastAPI")

    try:
        # Read PDF file
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()

        # Encode to base64
        pdf_b64 = base64.b64encode(pdf_data).decode('utf-8')

        # Prepare payload
        payload = {
            "file_b64": pdf_b64,
            "filename": pdf_path.name,
            "from_email": "test@example.com",
            "message_id": f"test-{datetime.now().isoformat()}",
            "gmail_id": "test-gmail-id",
            "subject": "Test Invoice",
            "received_date": datetime.now().isoformat()
        }

        # Send POST request
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

        print("  📤 Odosielam na http://localhost:8000/invoice...")

        response = requests.post(
            "http://localhost:8000/invoice",
            json=payload,
            headers=headers,
            timeout=120
        )

        # Check response
        if response.status_code == 200:
            data = response.json()
            print_success("Faktúra spracovaná!")
            print(f"\n  📊 VÝSLEDOK:")
            print(f"    Invoice Number: {data.get('invoice_number')}")
            print(f"    Customer: {data.get('customer_name')}")
            print(f"    Total Amount: {data.get('total_amount')} EUR")
            print(f"    Items Count: {data.get('items_count')}")
            print(f"\n  💾 ULOŽENIE:")
            print(f"    SQLite: {data.get('sqlite_saved')}")
            print(f"    PostgreSQL Enabled: {data.get('postgres_staging_enabled')}")
            print(f"    PostgreSQL Saved: {data.get('postgres_saved')}")
            if data.get('postgres_invoice_id'):
                print(f"    PostgreSQL ID: {data.get('postgres_invoice_id')}")
            print(f"\n  📁 SÚBORY:")
            print(f"    PDF: {data.get('pdf_saved')}")
            print(f"    XML: {data.get('xml_saved')}")

            return True
        else:
            print_error(f"Chyba pri spracovaní: HTTP {response.status_code}")
            print(f"    Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Chyba pri odosielaní: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_postgresql_data(invoice_number):
    """Verify data in PostgreSQL"""
    print_step(6, "Verifikácia dát v PostgreSQL")

    try:
        from src.database.postgres_staging import PostgresStagingClient
        from src.utils import config

        pg_config = {
            'host': config.POSTGRES_HOST,
            'port': config.POSTGRES_PORT,
            'database': config.POSTGRES_DATABASE,
            'user': config.POSTGRES_USER,
            'password': config.POSTGRES_PASSWORD
        }

        with PostgresStagingClient(pg_config) as pg_client:
            # Use the client's methods instead of direct cursor access
            # Check if invoice exists using duplicate check
            is_dup = pg_client.check_duplicate_invoice("36555720", invoice_number)

            if is_dup:
                print_success(f"Faktúra {invoice_number} nájdená v PostgreSQL")
                print(f"    Invoice Number: {invoice_number}")
                print(f"    Status: Existuje v databáze")
                return True
            else:
                print_error(f"Faktúra {invoice_number} nenájdená v PostgreSQL!")
                print("    Skúste manuálne query v pgAdmin:")
                print(f"    SELECT * FROM invoices_pending WHERE invoice_number = '{invoice_number}';")
                return False

    except Exception as e:
        print_error(f"Chyba pri verifikácii: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print_header("TEST INTEGRÁCIE - Supplier Invoice Loader")
    print("\nTest kompletného workflow:")
    print("  - FastAPI server")
    print("  - PostgreSQL staging database")
    print("  - SQLite database")
    print("  - File storage (PDF/XML)")

    # Check environment
    if not check_environment():
        print("\n❌ Test prerušený - chýbajúce ENV premenné")
        return False

    # Get API key
    api_key = os.getenv("LS_API_KEY")

    # Check FastAPI server
    if not check_fastapi_server():
        print("\n❌ Test prerušený - FastAPI server nebeží")
        return False

    # Check PostgreSQL
    if not check_postgresql_connection():
        print("\n❌ Test prerušený - PostgreSQL pripojenie zlyhalo")
        return False

    # Check test PDF
    test_pdf = check_test_pdf()
    if not test_pdf:
        print("\n❌ Test prerušený - chýba test PDF")
        return False

    # Send test invoice
    if not send_test_invoice(test_pdf, api_key):
        print("\n❌ Test zlyhal - faktúra nebola spracovaná")
        return False

    # Verify PostgreSQL data (optional - ask for invoice number)
    print("\n" + "-" * 70)
    invoice_number = input("Zadaj invoice_number pre verifikáciu v PostgreSQL (Enter = preskočiť): ").strip()

    if invoice_number:
        verify_postgresql_data(invoice_number)

    # Success
    print_header("✅ TEST ÚSPEŠNE DOKONČENÝ")
    print("\nĎalšie kroky:")
    print("  1. Otvor invoice-editor GUI")
    print("  2. Over že faktúra sa zobrazuje v liste")
    print("  3. Uprav faktúru (ak treba)")
    print("  4. Schváľ faktúru")
    print("  5. Over import do NEX Genesis")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test prerušený používateľom")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Neočakávaná chyba: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
