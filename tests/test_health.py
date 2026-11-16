from fastapi.testclient import TestClient
import pytest
from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] in {"ok", "unavailable", "not_configured"}


def test_health_station_count_matches_database_state():
    body = client.get("/health").json()

    if body["database"] == "ok":
        assert isinstance(body["stations_count"], int)
    else:
        assert body["stations_count"] is None


@pytest.mark.db
def test_health_reports_imported_station_count():
    assert client.get("/health").json()["stations_count"] == 387