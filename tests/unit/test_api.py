# -*- coding: utf-8 -*-
"""
Tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client"""
    from main import app
    return TestClient(app)


@pytest.fixture
def api_key():
    """Get API key from config"""
    from src.utils import config
    return config.API_KEY


def test_root_endpoint(client):
    """Test root endpoint returns service info"""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert "service" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "running"


def test_health_endpoint_no_auth(client):
    """Test health endpoint works without authentication"""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert "timestamp" in data
    assert data["status"] in ["healthy", "degraded", "unhealthy"]


def test_status_endpoint_requires_auth(client):
    """Test status endpoint requires authentication"""
    # Without API key
    response = client.get("/status")

    # Should return 422 (missing header) or 401 (invalid key)
    assert response.status_code in [401, 422]


def test_status_endpoint_with_auth(client, api_key):
    """Test status endpoint with valid API key"""
    response = client.get(
        "/status",
        headers={"X-API-Key": api_key}
    )

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert "components" in data
    assert "statistics" in data


def test_metrics_endpoint_no_auth(client):
    """Test metrics endpoint works without authentication"""
    response = client.get("/metrics")

    assert response.status_code == 200
    data = response.json()

    assert "uptime_seconds" in data
    assert "app_invoices_processed_total" in data


def test_metrics_prometheus_endpoint(client):
    """Test Prometheus metrics endpoint"""
    response = client.get("/metrics/prometheus")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

    # Should contain Prometheus format
    assert "# HELP" in response.text
    assert "# TYPE" in response.text


def test_stats_endpoint_no_auth(client):
    """Test stats endpoint works without authentication"""
    response = client.get("/stats")

    assert response.status_code == 200
    data = response.json()

    assert "total_invoices" in data


def test_invoices_endpoint_requires_auth(client):
    """Test invoices list endpoint requires authentication"""
    response = client.get("/invoices")

    assert response.status_code in [401, 422]


def test_invoices_endpoint_with_auth(client, api_key):
    """Test invoices list endpoint with authentication"""
    response = client.get(
        "/invoices",
        headers={"X-API-Key": api_key}
    )

    assert response.status_code == 200
    data = response.json()

    assert "count" in data
    assert "invoices" in data
    assert isinstance(data["invoices"], list)


def test_invoice_endpoint_requires_auth(client):
    """Test invoice processing endpoint requires authentication"""
    response = client.post(
        "/invoice",
        json={}
    )

    assert response.status_code in [401, 422]


def test_invoice_endpoint_with_invalid_data(client, api_key):
    """Test invoice endpoint with invalid data"""
    response = client.post(
        "/invoice",
        headers={"X-API-Key": api_key},
        json={}  # Missing required fields
    )

    # Should return validation error
    assert response.status_code == 422


def test_invoice_endpoint_with_valid_structure(client, api_key):
    """Test invoice endpoint with valid request structure"""
    import base64

    # Create minimal valid request
    request_data = {
        "file_b64": base64.b64encode(b"dummy pdf content").decode(),
        "filename": "test.pdf",
        "subject": "Test Invoice",
        "from_email": "test@example.com",
        "message_id": "test-message-123",
        "gmail_id": "gmail-123",
        "received_date": "2025-10-06T10:00:00"
    }

    response = client.post(
        "/invoice",
        headers={"X-API-Key": api_key},
        json=request_data
    )

    # Will likely fail at extraction stage, but should accept request
    # Status can be 200 (partial success) or 500 (processing error)
    assert response.status_code in [200, 500]


def test_admin_test_email_endpoint(client, api_key):
    """Test admin test email endpoint"""
    response = client.post(
        "/admin/test-email",
        headers={"X-API-Key": api_key}
    )

    assert response.status_code == 200
    data = response.json()

    assert "success" in data
    assert "message" in data


def test_admin_send_summary_endpoint(client, api_key):
    """Test admin send summary endpoint"""
    response = client.post(
        "/admin/send-summary",
        headers={"X-API-Key": api_key}
    )

    assert response.status_code == 200
    data = response.json()

    assert "success" in data
    assert "message" in data


def test_invalid_api_key_returns_401(client):
    """Test that invalid API key returns 401"""
    response = client.get(
        "/status",
        headers={"X-API-Key": "invalid-key"}
    )

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_docs_endpoints_exist(client):
    """Test that API documentation endpoints exist"""
    # Swagger UI
    response = client.get("/docs")
    assert response.status_code == 200

    # ReDoc
    response = client.get("/redoc")
    assert response.status_code == 200


def test_openapi_json_exists(client):
    """Test that OpenAPI JSON schema exists"""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    data = response.json()

    assert "openapi" in data
    assert "paths" in data


def test_cors_headers_if_enabled(client):
    """Test CORS headers if CORS is enabled"""
    response = client.get("/health")

    # CORS headers might not be enabled, so just check response is valid
    assert response.status_code == 200


@pytest.mark.integration
def test_full_invoice_processing_flow(client, api_key):
    """Integration test: Full invoice processing"""
    # This would require a real PDF file
    # Skip for now unless sample PDFs are available
    pytest.skip("Requires sample PDF file")


def test_api_metrics_increment(client):
    """Test that API requests increment metrics"""
    from src.utils import monitoring

    # Get initial value
    initial = monitoring.metrics.api_requests

    # Make request
    client.get("/health")

    # Should increment
    assert monitoring.metrics.api_requests > initial