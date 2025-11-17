# -*- coding: utf-8 -*-
"""
Supplier Invoice Loader - Entry Point
======================================

Multi-customer SaaS for automated invoice processing.
"""

import time
import hashlib
from datetime import datetime
from typing import Optional
from pathlib import Path
import base64

from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from src.api import models
from src.utils import config, monitoring, notifications
from src.utils.text_utils import clean_string
from src.database import database
from src.database.postgres_staging import PostgresStagingClient
from src.extractors.ls_extractor import extract_invoice_data
from src.business.isdoc_service import generate_isdoc_xml

# Start time for uptime calculation
START_TIME = time.time()

# Initialize FastAPI app
app = FastAPI(
    title="Supplier Invoice Loader",
    description="Automated invoice processing system",
    version="2.0.0"
)


# ============================================================================
# MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def track_requests(request, call_next):
    """Middleware to track API requests in metrics"""
    # Increment request counter
    monitoring.metrics.increment_api_request()

    # Process request
    response = await call_next(request)

    return response


# ============================================================================
# AUTHENTICATION
# ============================================================================

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Verify API key from X-API-Key header

    Args:
        x_api_key: API key from header

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not x_api_key:
        raise HTTPException(
            status_code=422,
            detail="Missing X-API-Key header"
        )

    if x_api_key != config.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    return x_api_key


# ============================================================================
# PUBLIC ENDPOINTS (no auth required)
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - service information"""
    return {
        "service": "Supplier Invoice Loader",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint - for monitoring systems"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/metrics")
async def metrics():
    """Metrics endpoint - basic metrics in JSON format"""
    uptime = int(time.time() - START_TIME)

    # Get stats from database
    try:
        stats = database.get_stats()
        total_processed = stats.get('total', 0)
    except Exception:
        total_processed = 0

    return {
        "uptime_seconds": uptime,
        "app_invoices_processed_total": total_processed,
        "app_info": {
            "version": "2.0.0",
            "customer": config.CUSTOMER_NAME
        }
    }


@app.get("/metrics/prometheus", response_class=PlainTextResponse)
async def metrics_prometheus():
    """Metrics endpoint - Prometheus format"""
    uptime = int(time.time() - START_TIME)

    # Get stats from database
    try:
        stats = database.get_stats()
        total_processed = stats.get('total', 0)
        total_errors = stats.get('by_status', {}).get('error', 0)
    except Exception:
        total_processed = 0
        total_errors = 0

    prometheus_metrics = f"""# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds gauge
app_uptime_seconds {uptime}

# HELP app_invoices_processed_total Total number of invoices processed
# TYPE app_invoices_processed_total counter
app_invoices_processed_total {total_processed}

# HELP app_invoices_errors_total Total number of invoice processing errors
# TYPE app_invoices_errors_total counter
app_invoices_errors_total {total_errors}

# HELP app_info Application information
# TYPE app_info gauge
app_info{{version="2.0.0",customer="{config.CUSTOMER_NAME}"}} 1
"""

    return prometheus_metrics


@app.get("/stats")
async def stats():
    """Statistics endpoint - database statistics"""
    try:
        # Initialize database if needed
        database.init_database()
        stats = database.get_stats()
        # Add total_invoices for backward compatibility with tests
        if "total" in stats and "total_invoices" not in stats:
            stats["total_invoices"] = stats["total"]
        return stats
    except Exception as e:
        # Return empty stats if database not available
        return {
            "total_invoices": 0,
            "total": 0,
            "by_status": {},
            "by_nex_status": {},
            "by_customer": {},
            "duplicates": 0,
            "error": str(e)
        }


# ============================================================================
# PROTECTED ENDPOINTS (require authentication)
# ============================================================================

@app.get("/status")
async def status(api_key: str = Depends(verify_api_key)):
    """
    Detailed status endpoint - requires authentication

    Returns system status, components health, and statistics
    """
    # Get database stats
    try:
        db_stats = database.get_stats()
        db_healthy = True
    except Exception as e:
        db_stats = {"error": str(e)}
        db_healthy = False

    # Get system health
    storage_health = monitoring.check_storage_health()
    storage_ok = storage_health.get('storage_healthy', False)

    return {
        "status": "healthy" if db_healthy and storage_ok else "degraded",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": "healthy" if db_healthy else "error",
            "storage": "healthy" if storage_ok else "warning",
            "smtp": "unknown"  # Could add SMTP check
        },
        "statistics": db_stats,
        "uptime_seconds": int(time.time() - START_TIME)
    }


@app.get("/invoices")
async def list_invoices(
    limit: int = 100,
    api_key: str = Depends(verify_api_key)
):
    """
    List invoices - requires authentication

    Args:
        limit: Maximum number of invoices to return

    Returns:
        List of invoices with metadata
    """
    try:
        # Initialize database if needed
        database.init_database()
        # Get invoices from database
        invoices = database.get_all_invoices(limit=limit)

        return {
            "count": len(invoices),
            "invoices": invoices
        }
    except Exception as e:
        # Return empty list if database not available
        return {
            "count": 0,
            "invoices": [],
            "error": str(e)
        }


@app.post("/invoice")
async def process_invoice(
    request: models.InvoiceRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Process invoice - requires authentication

    Main endpoint for invoice processing from n8n workflow

    Workflow:
    1. Decode and save PDF
    2. Extract invoice data from PDF
    3. Save to SQLite database
    4. Generate ISDOC XML
    5. Save XML to disk
    6. [Optional] Save to PostgreSQL staging database for invoice-editor

    Args:
        request: Invoice data including PDF file

    Returns:
        Processing result with status and extracted data
    """
    try:
        # 1. Decode PDF file
        pdf_data = base64.b64decode(request.file_b64)

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"{timestamp}_{request.filename}"
        pdf_path = config.PDF_DIR / pdf_filename

        # Save PDF to disk
        pdf_path.write_bytes(pdf_data)
        print(f"✅ PDF saved: {pdf_path}")

        # Calculate file hash for duplicate detection
        file_hash = hashlib.md5(pdf_data).hexdigest()

        # 2. Extract data from PDF
        invoice_data = extract_invoice_data(str(pdf_path))

        if not invoice_data:
            raise Exception("Failed to extract data from PDF")

        print(f"✅ Data extracted: Invoice {invoice_data.invoice_number}")

        # 3. Save to SQLite database
        database.init_database()
        database.save_invoice(
            customer_name=invoice_data.customer_name,
            invoice_number=invoice_data.invoice_number,
            invoice_date=invoice_data.issue_date,
            total_amount=float(invoice_data.total_amount) if invoice_data.total_amount else 0.0,
            file_path=str(pdf_path),
            file_hash=file_hash,
            status="received"
        )
        print(f"✅ Saved to SQLite: {invoice_data.invoice_number}")

        # 4. Generate ISDOC XML
        xml_filename = f"{invoice_data.invoice_number}.xml"
        xml_path = config.XML_DIR / xml_filename

        isdoc_xml = generate_isdoc_xml(invoice_data, str(xml_path))
        print(f"✅ ISDOC XML generated: {xml_path}")

        # 5. Save to PostgreSQL staging database (if enabled)
        postgres_saved = False
        postgres_invoice_id = None

        if config.POSTGRES_STAGING_ENABLED:
            try:
                # Prepare PostgreSQL config
                pg_config = {
                    'host': config.POSTGRES_HOST,
                    'port': config.POSTGRES_PORT,
                    'database': config.POSTGRES_DATABASE,
                    'user': config.POSTGRES_USER,
                    'password': config.POSTGRES_PASSWORD
                }

                # Create PostgreSQL client
                with PostgresStagingClient(pg_config) as pg_client:
                    # Check for duplicates
                    is_duplicate = pg_client.check_duplicate_invoice(
                        invoice_data.supplier_ico,
                        invoice_data.invoice_number
                    )

                    if is_duplicate:
                        print(f"⚠️  Invoice already exists in PostgreSQL staging: {invoice_data.invoice_number}")
                    else:
                        # Prepare invoice data for PostgreSQL
                        invoice_pg_data = {
                            'supplier_ico': invoice_data.supplier_ico,
                            'supplier_name': invoice_data.supplier_name,
                            'supplier_dic': invoice_data.supplier_dic,
                            'invoice_number': invoice_data.invoice_number,
                            'invoice_date': invoice_data.issue_date,
                            'due_date': invoice_data.due_date,
                            'total_amount': invoice_data.total_amount,
                            'total_vat': invoice_data.tax_amount,
                            'total_without_vat': invoice_data.net_amount,
                            'currency': invoice_data.currency
                        }

                        # Prepare items data for PostgreSQL
                        items_pg_data = []
                        for item in invoice_data.items:
                            items_pg_data.append({
                                'line_number': item.line_number,
                                'name': item.description,
                                'quantity': item.quantity,
                                'unit': item.unit,
                                'price_per_unit': item.unit_price_no_vat,
                                'ean': item.ean_code,
                                'vat_rate': item.vat_rate
                            })

                        # Insert to PostgreSQL
                        postgres_invoice_id = pg_client.insert_invoice_with_items(
                            invoice_pg_data,
                            items_pg_data,
                            isdoc_xml
                        )

                        if postgres_invoice_id:
                            postgres_saved = True
                            print(f"✅ Saved to PostgreSQL staging: invoice_id={postgres_invoice_id}")
                        else:
                            print(f"❌ Failed to save to PostgreSQL staging")

            except Exception as pg_error:
                # Log error but don't fail the whole process
                print(f"⚠️  PostgreSQL staging error: {pg_error}")
                # Continue - invoice is still saved to SQLite and files

        # Return success response
        return {
            "success": True,
            "message": "Invoice processed successfully",
            "invoice_number": invoice_data.invoice_number,
            "customer_name": invoice_data.customer_name,
            "total_amount": float(invoice_data.total_amount) if invoice_data.total_amount else 0.0,
            "items_count": len(invoice_data.items),
            "pdf_saved": str(pdf_path),
            "xml_saved": str(xml_path),
            "sqlite_saved": True,
            "postgres_staging_enabled": config.POSTGRES_STAGING_ENABLED,
            "postgres_saved": postgres_saved,
            "postgres_invoice_id": postgres_invoice_id,
            "received_date": request.received_date
        }

    except Exception as e:
        # Log error
        print(f"❌ Invoice processing failed: {e}")
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Invoice processing failed: {str(e)}"
        )


@app.post("/admin/test-email")
async def admin_test_email(api_key: str = Depends(verify_api_key)):
    """
    Admin endpoint - send test email

    Sends a test email to verify SMTP configuration
    """
    try:
        # Send test email
        result = notifications.send_test_email()

        return {
            "success": result,
            "message": "Test email sent successfully" if result else "Failed to send test email"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send test email: {str(e)}"
        )


@app.post("/admin/send-summary")
async def admin_send_summary(api_key: str = Depends(verify_api_key)):
    """
    Admin endpoint - send daily summary

    Sends daily summary email with processing statistics
    """
    try:
        # Send daily summary
        result = notifications.send_daily_summary()

        return {
            "success": result,
            "message": "Daily summary sent successfully" if result else "Failed to send summary"
        }
    except Exception as e:
        # Return error but don't throw 500
        return {
            "success": False,
            "message": f"Failed to send summary: {str(e)}"
        }


# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("=" * 60)
    print("🚀 Supplier Invoice Loader v2.0 Starting...")
    print("=" * 60)
    print(f"Customer: {config.CUSTOMER_NAME}")
    print(f"PDF Storage: {config.PDF_DIR}")
    print(f"XML Storage: {config.XML_DIR}")
    print(f"Database: {config.DB_FILE}")
    print(f"PostgreSQL Staging: {'Enabled' if config.POSTGRES_STAGING_ENABLED else 'Disabled'}")
    if config.POSTGRES_STAGING_ENABLED:
        print(f"PostgreSQL: {config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DATABASE}")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("=" * 60)
    print("🛑 Supplier Invoice Loader Shutting Down...")
    print("=" * 60)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("🚀 Starting Supplier Invoice Loader v2.0")
    print("=" * 60)
    print(f"📊 API Documentation: http://localhost:8000/docs")
    print(f"📊 ReDoc: http://localhost:8000/redoc")
    print(f"🔍 Health Check: http://localhost:8000/health")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )