"""
Supplier Invoice Loader - Entry Point
======================================

Multi-customer SaaS for automated invoice processing.
"""

from fastapi import FastAPI
from src.api import models
from src.utils import config, monitoring

# Initialize FastAPI app
app = FastAPI(
    title="Supplier Invoice Loader",
    description="Automated invoice processing system",
    version="2.0.0"
)

# Import routes (will be added in next phase)
# from src.api.routes import router
# app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Supplier Invoice Loader",
        "version": "2.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    # Load configuration
    # cfg = config.load_config()
    
    print("🚀 Starting Supplier Invoice Loader v2.0")
    print("📊 API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
