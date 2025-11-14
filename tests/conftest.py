# -*- coding: utf-8 -*-
"""
Pytest configuration and shared fixtures
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests (may send real emails, etc.)"
    )


def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory"""
    return Path(__file__).parent / "samples"


@pytest.fixture(scope="session")
def sample_invoice_data():
    """Sample invoice data for testing"""
    from src.extractors.ls_extractor import InvoiceData, InvoiceItem
    from decimal import Decimal

    invoice = InvoiceData(
        invoice_number="2025001",
        issue_date="2025-10-06",
        due_date="2025-10-20",
        total_amount=Decimal("1234.56"),
        tax_amount=Decimal("234.56"),
        net_amount=Decimal("1000.00"),
        currency="EUR",
        supplier_name="L & Š, s.r.o.",
        customer_name="Test Customer",
        customer_ico="12345678",
        iban="SK1234567890123456789012",
        variable_symbol="2025001"
    )

    # Add sample items
    invoice.items = [
        InvoiceItem(
            line_number=1,
            description="Test Product 1",
            quantity=Decimal("5"),
            unit="KS",
            unit_price_with_vat=Decimal("10.00"),
            total_with_vat=Decimal("50.00"),
            vat_rate=Decimal("20")
        ),
        InvoiceItem(
            line_number=2,
            description="Test Product 2",
            quantity=Decimal("10"),
            unit="KS",
            unit_price_with_vat=Decimal("20.00"),
            total_with_vat=Decimal("200.00"),
            vat_rate=Decimal("20")
        )
    ]

    return invoice


@pytest.fixture
def mock_config(monkeypatch):
    """Mock configuration for testing"""
    from src.utils from src.utils from src.utils import config

    # Mock sensitive values for testing
    monkeypatch.setattr(config, "API_KEY", "test-api-key-12345")
    monkeypatch.setattr(config, "CUSTOMER_NAME", "TESTCUSTOMER")
    monkeypatch.setattr(config, "ALERT_EMAIL", "test@example.com")
    monkeypatch.setattr(config, "SMTP_USER", "test@example.com")
    monkeypatch.setattr(config, "SMTP_PASSWORD", "test-password")

    return config


@pytest.fixture
def temp_database(tmp_path):
    """Create temporary database for testing"""
    import sqlite3

    db_path = tmp_path / "test_invoices.db"

    # Create database with schema
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_hash TEXT UNIQUE NOT NULL,
            pdf_path TEXT NOT NULL,
            xml_path TEXT,
            original_filename TEXT NOT NULL,
            message_id TEXT,
            gmail_id TEXT,
            sender TEXT,
            subject TEXT,
            received_date TEXT,
            invoice_number TEXT,
            issue_date TEXT,
            due_date TEXT,
            total_amount REAL,
            tax_amount REAL,
            net_amount REAL,
            variable_symbol TEXT,
            status TEXT DEFAULT 'pending',
            created_at INTEGER NOT NULL,
            processed_at INTEGER
        )
    """)

    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content (minimal valid PDF)"""
    # This is a minimal valid PDF
    return b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000274 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
366
%%EOF"""


@pytest.fixture
def mock_smtp_server(monkeypatch):
    """Mock SMTP server for email testing"""
    from unittest.mock import Mock, MagicMock
    import smtplib

    mock_server = MagicMock()
    mock_smtp = Mock(return_value=mock_server)

    monkeypatch.setattr(smtplib, "SMTP", mock_smtp)

    return mock_server


@pytest.fixture(autouse=True)
def reset_metrics():
    """Reset metrics before each test"""
    from src.utils from src.utils from src.utils import monitoring

    # Save original values
    original_metrics = monitoring.metrics

    yield

    # Reset to original or create new
    monitoring.metrics = monitoring.ApplicationMetrics()


@pytest.fixture
def api_client():
    """FastAPI test client"""
    from fastapi.testclient import TestClient
    from main import app

    return TestClient(app)


# Hooks for test reporting
def pytest_report_header(config):
    """Add custom header to pytest output"""
    return [
        "Supplier Invoice Loader - Test Suite",
        f"Python: {sys.version.split()[0]}",
        f"Pytest: {pytest.__version__}"
    ]