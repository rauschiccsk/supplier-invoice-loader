# -*- coding: utf-8 -*-
"""
Clear Test Data
===============

Clears test invoices from SQLite database for fresh testing.
"""

import sqlite3
from pathlib import Path
from src.utils import config


def clear_test_data():
    """Clear test invoices from database"""

    print("=" * 70)
    print("  Clear Test Data")
    print("=" * 70)
    print()

    db_file = config.DB_FILE

    if not Path(db_file).exists():
        print(f"✅ Database doesn't exist yet: {db_file}")
        return True

    print(f"Database: {db_file}")
    print()

    # Connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Count current invoices
    cursor.execute("SELECT COUNT(*) FROM invoices")
    count_before = cursor.fetchone()[0]

    print(f"Invoices before: {count_before}")

    if count_before == 0:
        print("✅ Database is already empty")
        conn.close()
        return True

    # Ask for confirmation
    print()
    print("⚠️  This will delete ALL invoices from database!")
    response = input("Continue? (yes/no): ").strip().lower()

    if response != "yes":
        print("❌ Cancelled by user")
        conn.close()
        return False

    # Delete all invoices
    cursor.execute("DELETE FROM invoices")
    conn.commit()

    # Count after
    cursor.execute("SELECT COUNT(*) FROM invoices")
    count_after = cursor.fetchone()[0]

    print(f"Invoices after: {count_after}")
    print(f"✅ Deleted: {count_before - count_after} invoices")

    conn.close()

    return True


def main():
    """Main function"""

    print()
    print("This script will clear all invoices from SQLite database.")
    print("Use this for fresh testing with the same test PDFs.")
    print()

    success = clear_test_data()

    if success:
        print()
        print("=" * 70)
        print("  ✅ COMPLETED")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Run test again: python scripts/test_invoice_integration.py")
        return True
    else:
        print()
        print("=" * 70)
        print("  ❌ CANCELLED")
        print("=" * 70)
        return False


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)