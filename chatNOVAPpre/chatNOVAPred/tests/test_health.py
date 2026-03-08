# tests/test_health.py

from fastapi.testclient import TestClient
from backend.main_novap import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/novap/health")

    assert response.status_code == 200

    data = response.json()

    assert data["ok"] is True
    assert data["module"] == "novap"
    assert data["status"] == "running"