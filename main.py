# -*- coding: utf-8 -*-
"""
Supplier Invoice Loader - Entry Point
======================================

Multi-customer SaaS for automated invoice processing.
"""

import time
from datetime import datetime
from typing import Optional
import base64

from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from src.api import models
from src.utils import config, monitoring, notifications
from src.database import database

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

    Args:
        request: Invoice data including PDF file

    Returns:
        Processing result with status and extracted data
    """
    try:
        # Decode PDF file
        pdf_data = base64.b64decode(request.file_b64)

        # TODO: Implement full processing pipeline
        # 1. Save PDF to disk
        # 2. Extract data from PDF
        # 3. Save to database
        # 4. Generate XML
        # 5. Send to NEX Genesis

        return {
            "success": True,
            "message": "Invoice processing started",
            "filename": request.filename,
            "received_date": request.received_date
        }
    except Exception as e:
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
