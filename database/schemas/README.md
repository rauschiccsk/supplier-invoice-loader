# Database Schemas

SQL migration scripts for supplier-invoice-loader database.

## Migration Files

- `001_initial_schema.sql` - Initial database structure v2.0

## How to Apply

### Manual Application
```bash
sqlite3 invoices.db < database/schemas/001_initial_schema.sql
```

### From Python
```python
from src.database.database import init_database
init_database()
```

---

**Note:** Migrations are applied automatically on application startup.
