# -*- coding: utf-8 -*-
"""
Supplier Invoice Loader - Database Operations v2.0
Enhanced with multi-customer support
"""

import sqlite3
import hashlib
import time
import logging
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

# Import customer name from config
try:
    from src.utils.config import DB_FILE, CUSTOMER_NAME
except ImportError:
    # Fallback for testing
    DB_FILE = Path("invoices.db")
    CUSTOMER_NAME = "DEFAULT"

logger = logging.getLogger(__name__)


def init_database():
    """Vytvorí databázovú štruktúru - v2.0 s multi-customer podporou"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Hlavná tabuľka faktúr - rozšírená o multi-customer polia
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Customer identification (NEW)
            customer_name TEXT,

            -- Email metadata
            message_id TEXT,
            gmail_id TEXT,
            sender TEXT,
            subject TEXT,
            received_date TEXT,

            -- File info
            file_hash TEXT UNIQUE NOT NULL,
            original_filename TEXT,
            pdf_path TEXT NOT NULL,
            xml_path TEXT,

            -- Timestamps
            created_at INTEGER NOT NULL,
            processed_at INTEGER,

            -- Status
            status TEXT DEFAULT 'received',

            -- NEX Genesis integration (NEW)
            nex_genesis_id TEXT,
            nex_status TEXT DEFAULT 'pending',
            nex_sync_date TEXT,
            nex_error_message TEXT,

            -- Extracted data (Fáza 2)
            invoice_number TEXT,
            issue_date TEXT,
            due_date TEXT,
            total_amount REAL,
            tax_amount REAL,
            net_amount REAL,
            variable_symbol TEXT,

            -- Flags
            is_duplicate INTEGER DEFAULT 0,

            -- Migration tracking (NEW)
            migration_version TEXT
        )
    """)

    # Indexy pre rýchle vyhľadávanie
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_hash ON invoices(file_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_id ON invoices(message_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoice_number ON invoices(invoice_number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON invoices(status)")

    # New indexes for multi-customer support
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_name ON invoices(customer_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nex_genesis_id ON invoices(nex_genesis_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nex_status ON invoices(nex_status)")

    conn.commit()
    conn.close()
    logger.info("Database initialized successfully (v2.0)")


def calculate_file_hash(file_content: bytes) -> str:
    """Vypočíta SHA-256 hash súboru"""
    return hashlib.sha256(file_content).hexdigest()


def is_duplicate(file_hash: str, message_id: Optional[str] = None, customer_name: Optional[str] = None) -> bool:
    """
    Skontroluje či faktúra už existuje v databáze
    V2.0: Kontroluje duplicity v rámci zákazníka

    Args:
        file_hash: SHA-256 hash PDF súboru
        message_id: Gmail message ID (optional)
        customer_name: Meno zákazníka (optional, default from config)

    Returns:
        True ak faktúra už existuje
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Use customer from config if not provided
    if customer_name is None:
        customer_name = CUSTOMER_NAME

    # Check by file hash (primary) within customer
    cursor.execute(
        "SELECT id FROM invoices WHERE file_hash = ? AND customer_name = ?",
        (file_hash, customer_name)
    )
    result = cursor.fetchone()

    # Check by message_id (secondary) within customer
    if not result and message_id:
        cursor.execute(
            "SELECT id FROM invoices WHERE message_id = ? AND customer_name = ?",
            (message_id, customer_name)
        )
        result = cursor.fetchone()

    conn.close()
    return result is not None


def insert_invoice(
        file_hash: str,
        pdf_path: str,
        original_filename: str,
        message_id: Optional[str] = None,
        gmail_id: Optional[str] = None,
        sender: Optional[str] = None,
        subject: Optional[str] = None,
        received_date: Optional[str] = None,
        customer_name: Optional[str] = None,
        nex_genesis_id: Optional[str] = None
) -> int:
    """
    Vloží novú faktúru do databázy
    V2.0: Pridaná podpora pre customer_name a nex_genesis_id

    Returns:
        ID novej faktúry
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Use customer from config if not provided
    if customer_name is None:
        customer_name = CUSTOMER_NAME

    cursor.execute("""
        INSERT INTO invoices (
            customer_name,
            message_id, gmail_id, sender, subject, received_date,
            file_hash, original_filename, pdf_path,
            created_at, status,
            nex_genesis_id, nex_status,
            migration_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        customer_name,
        message_id, gmail_id, sender, subject, received_date,
        file_hash, original_filename, pdf_path,
        int(time.time()), 'received',
        nex_genesis_id, 'pending' if not nex_genesis_id else 'synced',
        '2.0.0'
    ))

    invoice_id = cursor.lastrowid
    conn.commit()
    conn.close()

    logger.info(f"Invoice inserted: ID={invoice_id}, customer={customer_name}, hash={file_hash[:8]}...")
    return invoice_id


def update_nex_genesis_status(
        invoice_id: int,
        nex_genesis_id: str,
        status: str = 'synced',
        error_message: Optional[str] = None
) -> bool:
    """
    Update NEX Genesis sync status

    Args:
        invoice_id: Invoice ID in local database
        nex_genesis_id: ID from NEX Genesis system
        status: Sync status ('synced', 'error', 'pending')
        error_message: Error message if sync failed

    Returns:
        True if updated successfully
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE invoices SET
            nex_genesis_id = ?,
            nex_status = ?,
            nex_sync_date = ?,
            nex_error_message = ?
        WHERE id = ?
    """, (
        nex_genesis_id,
        status,
        datetime.now().isoformat(),
        error_message,
        invoice_id
    ))

    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        logger.info(f"NEX Genesis status updated: invoice_id={invoice_id}, nex_id={nex_genesis_id}, status={status}")
    else:
        logger.warning(f"Failed to update NEX Genesis status for invoice_id={invoice_id}")

    return success


def get_invoice_by_id(invoice_id: int) -> Optional[Dict]:
    """Vráti faktúru podľa ID"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
    row = cursor.fetchone()

    conn.close()

    if row:
        return dict(row)
    return None


def get_invoice_by_nex_id(nex_genesis_id: str) -> Optional[Dict]:
    """
    Vráti faktúru podľa NEX Genesis ID

    Args:
        nex_genesis_id: NEX Genesis ID

    Returns:
        Invoice dict or None
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM invoices WHERE nex_genesis_id = ?", (nex_genesis_id,))
    row = cursor.fetchone()

    conn.close()

    if row:
        return dict(row)
    return None


def get_all_invoices(limit: int = 100, customer_name: Optional[str] = None) -> List[Dict]:
    """
    Vráti zoznam faktúr
    V2.0: Možnosť filtrovať podľa zákazníka

    Args:
        limit: Max počet faktúr
        customer_name: Filter podľa zákazníka (None = všetci)

    Returns:
        List of invoice dicts
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if customer_name:
        cursor.execute("""
            SELECT * FROM invoices 
            WHERE customer_name = ?
            ORDER BY created_at DESC 
            LIMIT ?
        """, (customer_name, limit))
    else:
        cursor.execute("""
            SELECT * FROM invoices 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_pending_nex_sync(customer_name: Optional[str] = None, limit: int = 10) -> List[Dict]:
    """
    Get invoices pending NEX Genesis sync

    Args:
        customer_name: Filter by customer (None = all)
        limit: Max number of results

    Returns:
        List of invoices pending sync
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if customer_name:
        cursor.execute("""
            SELECT * FROM invoices 
            WHERE nex_status = 'pending' AND customer_name = ?
            ORDER BY created_at ASC 
            LIMIT ?
        """, (customer_name, limit))
    else:
        cursor.execute("""
            SELECT * FROM invoices 
            WHERE nex_status = 'pending'
            ORDER BY created_at ASC 
            LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_stats(customer_name: Optional[str] = None) -> Dict:
    """
    Vráti štatistiky o faktúrach
    V2.0: Možnosť získať štatistiky pre konkrétneho zákazníka

    Args:
        customer_name: Filter podľa zákazníka (None = všetci)

    Returns:
        Statistics dict
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Build WHERE clause
    where_clause = ""
    params = []
    if customer_name:
        where_clause = "WHERE customer_name = ?"
        params.append(customer_name)

    # Total count
    cursor.execute(f"SELECT COUNT(*) FROM invoices {where_clause}", params)
    total = cursor.fetchone()[0]

    # By status
    cursor.execute(f"""
        SELECT status, COUNT(*) 
        FROM invoices 
        {where_clause}
        GROUP BY status
    """, params)
    by_status = dict(cursor.fetchall())

    # By NEX sync status
    cursor.execute(f"""
        SELECT nex_status, COUNT(*) 
        FROM invoices 
        {where_clause}
        GROUP BY nex_status
    """, params)
    by_nex_status = dict(cursor.fetchall())

    # Duplicates
    cursor.execute(
        f"SELECT COUNT(*) FROM invoices {where_clause} {'AND' if where_clause else 'WHERE'} is_duplicate = 1", params)
    duplicates = cursor.fetchone()[0]

    # By customer (if not filtered)
    if not customer_name:
        cursor.execute("""
            SELECT customer_name, COUNT(*) 
            FROM invoices 
            GROUP BY customer_name
        """)
        by_customer = dict(cursor.fetchall())
    else:
        by_customer = {customer_name: total}

    conn.close()

    return {
        "total": total,
        "by_status": by_status,
        "by_nex_status": by_nex_status,
        "by_customer": by_customer,
        "duplicates": duplicates,
        "filter": customer_name
    }


def get_customer_list() -> List[str]:
    """
    Get list of all customers in database

    Returns:
        List of unique customer names
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT customer_name 
        FROM invoices 
        WHERE customer_name IS NOT NULL
        ORDER BY customer_name
    """)

    customers = [row[0] for row in cursor.fetchall()]
    conn.close()

    return customers




def save_invoice(
        customer_name: str,
        invoice_number: str,
        invoice_date: str,
        total_amount: float,
        file_path: str,
        file_hash: str,
        status: str = "received",
        message_id: Optional[str] = None,
        gmail_id: Optional[str] = None
) -> int:
    """
    Save invoice to database (simplified wrapper for insert_invoice)

    Args:
        customer_name: Customer name
        invoice_number: Invoice number
        invoice_date: Invoice date
        total_amount: Total amount
        file_path: Path to PDF file
        file_hash: File hash
        status: Invoice status
        message_id: Email message ID
        gmail_id: Gmail ID

    Returns:
        Invoice ID
    """
    # Insert invoice
    invoice_id = insert_invoice(
        file_hash=file_hash,
        pdf_path=file_path,
        original_filename=Path(file_path).name,
        message_id=message_id,
        gmail_id=gmail_id,
        customer_name=customer_name
    )

    # Update with extracted data
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE invoices SET
            invoice_number = ?,
            issue_date = ?,
            total_amount = ?,
            status = ?
        WHERE id = ?
    """, (
        invoice_number,
        invoice_date,
        total_amount,
        status,
        invoice_id
    ))

    conn.commit()
    conn.close()

    logger.info(f"Invoice saved: ID={invoice_id}, number={invoice_number}, amount={total_amount}")
    return invoice_id


# Backward compatibility - keep old function signatures working
def get_all_invoices_legacy(limit: int = 100) -> List[Dict]:
    """Legacy function for backward compatibility"""
    return get_all_invoices(limit, customer_name=CUSTOMER_NAME)


def get_stats_legacy() -> Dict:
    """Legacy function for backward compatibility"""
    return get_stats(customer_name=CUSTOMER_NAME)