# -*- coding: utf-8 -*-
"""
Supplier Invoice Loader - Configuration Template
Copy this file to config_customer.py and fill in customer-specific values

================================================================================
CONFIGURATION PARAMETERS EXPLAINED
================================================================================

CUSTOMER SPECIFIC PARAMETERS:
------------------------------

CUSTOMER_NAME (str):
    Short identifier for customer (no spaces), e.g. "MAGERSTAV", "ANDROS"
    Used in logs and monitoring alerts
    Example: "MAGERSTAV"

CUSTOMER_FULL_NAME (str):
    Full legal company name, e.g. "MÁGERSTAV, spol. s r.o."
    Used in ISDOC XML generation and official documents
    Example: "MÁGERSTAV, spol. s r.o."

NEX_GENESIS_API_URL (str):
    Base URL of customer's NEX Genesis API server
    Example: "http://192.168.1.100:8080/api" or "https://nex.customer.com/api"
    Must be accessible from this Python server
    Note: Do not include trailing slash

NEX_GENESIS_API_KEY (str):
    API authentication key provided by NEX Genesis
    Keep this secret! Never commit to Git.
    Use environment variable in production: os.getenv("NEX_API_KEY")
    Example: "nex_prod_abc123xyz789"

OPERATOR_EMAIL (str):
    Email address of operator who forwards invoices
    Example: "operator@customer.sk"
    Used for validation - only emails from this address are processed
    Multiple operators: use comma-separated list (future feature)

AUTOMATION_EMAIL (str):
    Email address where operator sends invoices for processing
    Example: "automation-magerstav@isnex.ai"
    Must be unique per customer
    This email must be set up in n8n workflow

ALERT_EMAIL (str):
    Email where system sends error alerts and notifications
    Usually support@icc.sk or customer's IT contact
    Example: "it@customer.sk" or "support@icc.sk"
    Multiple recipients: use comma-separated list

SEND_DAILY_SUMMARY (bool):
    If True, sends daily summary email with processing statistics
    Summary includes: processed invoices, errors, totals
    Sent daily at 23:55 (configurable in cron)
    Example: True

HEARTBEAT_ENABLED (bool):
    If True, enables /health endpoint monitoring
    Allows external monitoring systems (Uptime Robot, Pingdom) to check status
    Example: True


GENERIC PARAMETERS (usually don't need changes):
------------------------------------------------

API_KEY (str):
    API key for securing the FastAPI endpoints
    Default: from environment variable LS_API_KEY
    Production: MUST be changed! Use strong random key
    Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
    Example: "prod_key_XyZ123AbC456DeF789"

BASE_DIR (Path):
    Base directory of the application (auto-detected)
    Contains: main.py, config.py, database, logs
    Default: Directory where config.py is located
    Do not change unless you know what you're doing

STORAGE_BASE (Path):
    Root directory for storing PDFs and XMLs
    Default: C:\\NEX_INVOICES (Windows) or /opt/nex_invoices (Linux)
    Override with environment variable: LS_STORAGE_PATH
    Example: Path(r"D:\\InvoiceStorage") or Path("/mnt/storage/invoices")
    Note: Must have write permissions

PDF_DIR (Path):
    Directory for storing received PDF invoices
    Default: STORAGE_BASE/PDF
    Created automatically if doesn't exist
    Structure: flat (all PDFs in one folder with timestamps)

XML_DIR (Path):
    Directory for storing generated ISDOC XML files
    Default: STORAGE_BASE/XML
    Created automatically if doesn't exist
    XML files named by invoice number: {invoice_number}.xml

DB_FILE (Path):
    SQLite database file path
    Default: BASE_DIR/invoices.db
    Contains: invoice metadata, processing status, duplicates detection
    Backup regularly! Contains all historical data

LOG_FILE (Path):
    Application log file path
    Default: BASE_DIR/invoice_loader.log
    Rotation: manual (implement logrotate or Python logging handlers)
    Level: controlled by LOG_LEVEL parameter

LOG_LEVEL (str):
    Logging level for the application
    Values: DEBUG, INFO, WARNING, ERROR, CRITICAL
    Default: INFO
    Override with environment variable: LOG_LEVEL
    Production: INFO or WARNING
    Development/Debugging: DEBUG
    Example: "INFO"


SMTP CONFIGURATION (for email alerts and notifications):
--------------------------------------------------------

SMTP_HOST (str):
    SMTP server hostname
    Default: "smtp.gmail.com" (Gmail)
    For other providers:
        - Outlook: "smtp-mail.outlook.com"
        - Office365: "smtp.office365.com"
        - Custom: "mail.yourcompany.com"
    Example: "smtp.gmail.com"

SMTP_PORT (int):
    SMTP server port
    Common ports:
        - 587: TLS/STARTTLS (recommended)
        - 465: SSL
        - 25: Unencrypted (not recommended)
    Default: 587
    Example: 587

SMTP_USER (str):
    SMTP username (usually email address)
    Default: from environment variable SMTP_USER
    For Gmail: full email address (e.g., "automation@gmail.com")
    Security: NEVER hardcode! Use environment variables
    Example: os.getenv("SMTP_USER", "")

SMTP_PASSWORD (str):
    SMTP password or app-specific password
    Default: from environment variable SMTP_PASSWORD
    For Gmail: Use App Password (not regular password)
        - Enable 2FA on Gmail account
        - Generate App Password: https://myaccount.google.com/apppasswords
    Security: NEVER hardcode! Use environment variables
    Example: os.getenv("SMTP_PASSWORD", "")

SMTP_FROM (str):
    "From" email address for sent emails
    Default: "noreply@icc.sk"
    Should match SMTP_USER or be authorized sender
    Example: "automation@isnex.ai"


================================================================================
ENVIRONMENT VARIABLES
================================================================================

The following environment variables are supported:

Required in production:
    LS_API_KEY          - API key for FastAPI endpoints
    SMTP_USER           - SMTP username for email alerts
    SMTP_PASSWORD       - SMTP password for email alerts
    POSTGRES_PASSWORD   - PostgreSQL password for staging database (if enabled)

Optional:
    LS_STORAGE_PATH     - Override default storage location
    LOG_LEVEL           - Override default logging level (DEBUG/INFO/WARNING)
    NEX_API_KEY         - NEX Genesis API key (alternative to config file)

Setting environment variables:

Windows (PowerShell):
    $env:LS_API_KEY = "your-secret-key"
    $env:SMTP_USER = "automation@gmail.com"
    $env:SMTP_PASSWORD = "your-app-password"

Windows (CMD):
    set LS_API_KEY=your-secret-key
    set SMTP_USER=automation@gmail.com
    set SMTP_PASSWORD=your-app-password

Linux/Mac:
    export LS_API_KEY="your-secret-key"
    export SMTP_USER="automation@gmail.com"
    export SMTP_PASSWORD="your-app-password"

.env file (recommended for development):
    Create .env file in project root:
    LS_API_KEY=your-secret-key
    SMTP_USER=automation@gmail.com
    SMTP_PASSWORD=your-app-password


================================================================================
DEPLOYMENT CHECKLIST
================================================================================

Before deploying to a new customer:

1. Copy this file to config_customer.py
2. Fill in all CUSTOMER SPECIFIC parameters
3. Set environment variables (LS_API_KEY, SMTP credentials)
4. Test storage paths (PDF_DIR, XML_DIR must be writable)
5. Verify NEX_GENESIS_API_URL is accessible from server
6. Test email alerts (check SMTP settings)
7. Add config_customer.py to .gitignore
8. Never commit secrets to Git!


================================================================================
SECURITY BEST PRACTICES
================================================================================

1. API Keys:
   - Use strong random keys (32+ characters)
   - Rotate keys periodically
   - Use environment variables in production
   - Never commit to Git

2. SMTP Credentials:
   - Use app-specific passwords (not main password)
   - Enable 2FA on email account
   - Store in environment variables only

3. NEX Genesis API:
   - Use HTTPS in production
   - Restrict API access by IP if possible
   - Monitor API usage

4. File Permissions:
   - PDF_DIR, XML_DIR: read/write for app user only
   - config_customer.py: read-only, restricted access
   - DB_FILE: backup regularly, restrict access

5. Network:
   - Use firewall to restrict FastAPI port (8000)
   - Consider reverse proxy (nginx) for HTTPS
   - Monitor access logs


================================================================================
TROUBLESHOOTING
================================================================================

Problem: "config_customer.py not found"
Solution: Copy config_template.py to config_customer.py and fill values

Problem: "Permission denied" when saving PDF
Solution: Check STORAGE_BASE path exists and has write permissions
    Windows: icacls C:\\NEX_INVOICES /grant Users:F
    Linux: chmod 755 /opt/nex_invoices

Problem: Email alerts not working
Solution:
    1. Check SMTP_HOST, SMTP_PORT are correct
    2. Verify SMTP_USER, SMTP_PASSWORD environment variables are set
    3. For Gmail: generate App Password, enable "Less secure app access"
    4. Test with: telnet smtp.gmail.com 587

Problem: "Invalid API key" error
Solution:
    1. Check X-API-Key header in n8n matches config.API_KEY
    2. Verify environment variable LS_API_KEY is set
    3. Restart application after changing API key

Problem: NEX Genesis API connection failed
Solution:
    1. Verify NEX_GENESIS_API_URL is correct (no trailing slash)
    2. Check network connectivity: ping nex-server
    3. Verify API key is correct
    4. Check NEX Genesis logs for rejected requests

Problem: Database locked error
Solution:
    1. Only one process should access DB at a time
    2. Check for hung processes: tasklist | findstr python
    3. Restart application
    4. Consider WAL mode for SQLite (future improvement)


================================================================================
EXAMPLE CONFIGURATIONS
================================================================================

Example 1: MÁGERSTAV (production):
    CUSTOMER_NAME = "MAGERSTAV"
    CUSTOMER_FULL_NAME = "MÁGERSTAV, spol. s r.o."
    NEX_GENESIS_API_URL = "http://192.168.1.50:8080/api"
    OPERATOR_EMAIL = "uctaren@magerstav.sk"
    AUTOMATION_EMAIL = "automation-magerstav@isnex.ai"
    ALERT_EMAIL = "it@magerstav.sk,support@icc.sk"

Example 2: Development/Testing:
    CUSTOMER_NAME = "TESTCLIENT"
    CUSTOMER_FULL_NAME = "Test Client s.r.o."
    NEX_GENESIS_API_URL = "http://localhost:8080/api"
    OPERATOR_EMAIL = "test@localhost"
    AUTOMATION_EMAIL = "automation-test@localhost"
    ALERT_EMAIL = "developer@icc.sk"
    SEND_DAILY_SUMMARY = False
    HEARTBEAT_ENABLED = True

Example 3: Multi-location customer:
    CUSTOMER_NAME = "ANDROS_BA"
    CUSTOMER_FULL_NAME = "ANDROS Bratislava, s.r.o."
    STORAGE_BASE = Path(r"D:\\Invoices\ANDROS_BA")
    NEX_GENESIS_API_URL = "https://nex-ba.andros.sk/api"

"""

import os
from pathlib import Path

# ============================================================================
# CUSTOMER SPECIFIC CONFIGURATION - EDIT THESE VALUES
# ============================================================================

# Customer identification
CUSTOMER_NAME = "CUSTOMER_NAME_HERE"  # e.g. "MAGERSTAV"
CUSTOMER_FULL_NAME = "Customer Company Name s.r.o."

# NEX Genesis API
NEX_GENESIS_API_URL = "http://localhost:8080/api"  # Change to customer server
NEX_GENESIS_API_KEY = "CHANGE_ME_SECRET_KEY"

# Operator email (who forwards invoices)
OPERATOR_EMAIL = "operator@customer.sk"

# Automation email (where operator sends invoices)
AUTOMATION_EMAIL = "automation-customer@isnex.ai"

# Monitoring & Alerts
ALERT_EMAIL = "support@icc.sk"
SEND_DAILY_SUMMARY = True
HEARTBEAT_ENABLED = True



POSTGRESQL STAGING CONFIGURATION (for invoice-editor integration):
------------------------------------------------------------------

POSTGRES_STAGING_ENABLED (bool):
    Enable/disable PostgreSQL staging database integration
    If True: Invoices are saved to PostgreSQL for invoice-editor approval
    If False: Only SQLite database and file storage (legacy mode)
    Default: True
    Example: True

POSTGRES_HOST (str):
    PostgreSQL server hostname or IP address
    Default: "localhost"
    Example: "localhost"

POSTGRES_PORT (int):
    PostgreSQL server port
    Default: 5432 (standard PostgreSQL port)
    Example: 5432

POSTGRES_DATABASE (str):
    PostgreSQL database name
    Default: "invoice_staging"
    Example: "invoice_staging"

POSTGRES_USER (str):
    PostgreSQL username for connection
    Default: "invoice_user"
    Example: "invoice_user"

POSTGRES_PASSWORD (str):
    PostgreSQL user password
    Default: from environment variable POSTGRES_PASSWORD
    Security: NEVER hardcode! Use environment variables
    Example: os.getenv("POSTGRES_PASSWORD", "")


# ============================================================================
# GENERIC CONFIGURATION - DO NOT CHANGE (unless you know what you're doing)
# ============================================================================

# API Security
API_KEY = os.getenv("LS_API_KEY", "ls-dev-key-change-in-production-2025")

# Paths
BASE_DIR = Path(__file__).resolve().parent

# Storage paths
STORAGE_BASE = Path(os.getenv("LS_STORAGE_PATH", r"C:\NEX_INVOICES"))
PDF_DIR = STORAGE_BASE / "PDF"
XML_DIR = STORAGE_BASE / "XML"

# Create directories
PDF_DIR.mkdir(parents=True, exist_ok=True)
XML_DIR.mkdir(parents=True, exist_ok=True)

# Database
DB_FILE = BASE_DIR / "invoices.db"

# Logging
LOG_FILE = BASE_DIR / "invoice_loader.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# SMTP Configuration for email alerts
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = "noreply@icc.sk"

# ============================================================================
# POSTGRESQL STAGING CONFIGURATION (invoice-editor integration)
# ============================================================================

# Enable PostgreSQL staging database integration
POSTGRES_STAGING_ENABLED = True  # Set False to disable invoice-editor integration

# PostgreSQL connection settings
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DATABASE = "invoice_staging"
POSTGRES_USER = "invoice_user"
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
