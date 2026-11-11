from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] in {"ok", "unavailable", "not_configured"}


def test_health_reports_station_count_only_with_database():
    body = client.get("/health").json()

    if body["database"] == "ok":
        assert body["stations_count"] == 387
    else:
        assert body["stations_count"] is None
