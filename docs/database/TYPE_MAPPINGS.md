# Database Type Mappings

**Project:** supplier-invoice-loader  
**Database:** SQLite 3.x

---

## Python → SQLite Type Mapping

| Python Type | SQLite Type | Notes |
|------------|-------------|-------|
| `str` | `TEXT` | UTF-8 encoded |
| `int` | `INTEGER` | 64-bit signed |
| `float` | `REAL` | 64-bit IEEE floating point |
| `bool` | `INTEGER` | 0 = False, 1 = True |
| `bytes` | `BLOB` | Binary data |
| `datetime` | `TEXT` | ISO 8601 format |
| `None` | `NULL` | |

---

## Table: invoices

Multi-customer support v2.0 schema.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary key |
| `customer_name` | TEXT | YES | NULL | Customer identifier |
| `message_id` | TEXT | YES | NULL | Email message ID |
| `gmail_id` | TEXT | YES | NULL | Gmail ID |
| `sender` | TEXT | YES | NULL | Sender email |
| `subject` | TEXT | YES | NULL | Email subject |
| `received_date` | TEXT | YES | NULL | Email received date |
| `file_hash` | TEXT | NO | - | SHA-256 hash (UNIQUE) |
| `original_filename` | TEXT | YES | NULL | Original PDF filename |
| `pdf_path` | TEXT | NO | - | Path to PDF file |
| `xml_path` | TEXT | YES | NULL | Path to XML file |
| `created_at` | INTEGER | NO | - | Unix timestamp |
| `processed_at` | INTEGER | YES | NULL | Unix timestamp |
| `status` | TEXT | YES | 'received' | Processing status |
| `nex_genesis_id` | TEXT | YES | NULL | NEX Genesis ID |
| `nex_status` | TEXT | YES | 'pending' | NEX sync status |
| `nex_sync_date` | TEXT | YES | NULL | Last sync date |
| `nex_error_message` | TEXT | YES | NULL | Error message |
| `invoice_number` | TEXT | YES | NULL | Extracted invoice # |
| `issue_date` | TEXT | YES | NULL | Invoice issue date |
| `due_date` | TEXT | YES | NULL | Invoice due date |
| `total_amount` | REAL | YES | NULL | Total amount |
| `tax_amount` | REAL | YES | NULL | Tax amount |
| `net_amount` | REAL | YES | NULL | Net amount |
| `variable_symbol` | TEXT | YES | NULL | Variable symbol |
| `is_duplicate` | INTEGER | YES | 0 | Duplicate flag |
| `migration_version` | TEXT | YES | NULL | Migration tracking |

---

## Indexes

```sql
CREATE INDEX idx_file_hash ON invoices(file_hash);
CREATE INDEX idx_message_id ON invoices(message_id);
CREATE INDEX idx_invoice_number ON invoices(invoice_number);
CREATE INDEX idx_status ON invoices(status);
CREATE INDEX idx_customer_name ON invoices(customer_name);
CREATE INDEX idx_nex_genesis_id ON invoices(nex_genesis_id);
CREATE INDEX idx_nex_status ON invoices(nex_status);
```

---

## Status Values

### Processing Status
- `received` - Initial state after PDF received
- `processed` - Successfully processed
- `error` - Processing failed
- `partial` - Partial success (e.g., PDF saved but extraction failed)

### NEX Sync Status
- `pending` - Not yet synced to NEX Genesis
- `synced` - Successfully synced
- `error` - Sync failed

---

**Generated:** 2025-11-13
