"""
Unit Tests for REST API

Tests API endpoints, request/response validation, and error handling.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from api.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and root endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "AEO Multi-Agent API"
        assert data["version"] == "1.5.0"
        assert "endpoints" in data

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.5.0"
        assert "timestamp" in data


class TestCampaignEndpoints:
    """Test campaign creation and management endpoints."""

    def test_create_campaign_valid(self):
        """Test creating campaign with valid request."""
        request_data = {
            "url": "https://example.com/article",
            "mode": "balanced",
            "industry": "SaaS",
            "optimization_level": "balanced",
            "tracking_duration_days": 30,
            "queries": ["test query"]
        }

        response = client.post("/api/campaigns", json=request_data)
        assert response.status_code == 202
        data = response.json()
        assert "campaign_id" in data
        assert data["status"] in ["pending", "running"]
        assert "created_at" in data

    def test_create_campaign_invalid_url(self):
        """Test campaign creation with invalid URL."""
        request_data = {
            "url": "not-a-valid-url",
            "mode": "balanced"
        }

        response = client.post("/api/campaigns", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_create_campaign_invalid_mode(self):
        """Test campaign creation with invalid mode."""
        request_data = {
            "url": "https://example.com",
            "mode": "invalid_mode"
        }

        response = client.post("/api/campaigns", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_create_campaign_invalid_duration(self):
        """Test campaign creation with invalid duration."""
        request_data = {
            "url": "https://example.com",
            "tracking_duration_days": 500  # > 365
        }

        response = client.post("/api/campaigns", json=request_data)
        assert response.status_code == 422  # Validation error


class TestCompetitiveEndpoints:
    """Test competitive analysis endpoints."""

    def test_create_competitive_analysis_valid(self):
        """Test creating competitive analysis with valid request."""
        request_data = {
            "topic": "project management",
            "competitor_urls": [
                "https://competitor1.com",
                "https://competitor2.com"
            ],
            "region": "US"
        }

        response = client.post("/api/competitive", json=request_data)
        assert response.status_code == 202
        data = response.json()
        assert "analysis_id" in data
        assert data["status"] in ["pending", "running"]

    def test_create_competitive_no_competitors(self):
        """Test competitive analysis with no competitors."""
        request_data = {
            "topic": "test",
            "competitor_urls": []
        }

        response = client.post("/api/competitive", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_create_competitive_too_many_competitors(self):
        """Test competitive analysis with too many competitors."""
        request_data = {
            "topic": "test",
            "competitor_urls": [f"https://comp{i}.com" for i in range(15)]  # > 10
        }

        response = client.post("/api/competitive", json=request_data)
        assert response.status_code == 422  # Validation error


class TestMonitoringEndpoints:
    """Test monitoring setup endpoints."""

    def test_setup_monitoring_valid(self):
        """Test setting up monitoring with valid request."""
        request_data = {
            "url": "https://example.com/article",
            "duration_days": 90,
            "alert_on_changes": True
        }

        response = client.post("/api/monitoring", json=request_data)
        assert response.status_code == 202
        data = response.json()
        assert "monitor_id" in data
        assert data["status"] in ["pending", "running"]

    def test_setup_monitoring_invalid_duration(self):
        """Test monitoring with invalid duration."""
        request_data = {
            "url": "https://example.com",
            "duration_days": 0  # < 1
        }

        response = client.post("/api/monitoring", json=request_data)
        assert response.status_code == 422  # Validation error


class TestStatusEndpoints:
    """Test status and listing endpoints."""

    def test_list_campaigns(self):
        """Test listing all campaigns."""
        response = client.get("/api/campaigns")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_workflow_status_not_found(self):
        """Test getting status for non-existent workflow."""
        response = client.get("/api/status/nonexistent_id")
        assert response.status_code == 404

    def test_delete_campaign_not_found(self):
        """Test deleting non-existent campaign."""
        response = client.delete("/api/campaigns/nonexistent_id")
        assert response.status_code == 404


class TestAPIDocumentation:
    """Test API documentation endpoints."""

    def test_openapi_schema(self):
        """Test OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "AEO Multi-Agent API"
        assert schema["info"]["version"] == "1.5.0"

    def test_swagger_docs(self):
        """Test Swagger UI is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_docs(self):
        """Test ReDoc is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
