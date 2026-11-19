"""Testy endpointów na danych przykładowych (zgodność z docs/api-contract.md).

/stations, /stations/nearest, odjazdy i /stats biorą dane z bazy, więc ich testy są
w tests/test_stations_db.py, tests/test_departures_db.py i tests/test_stats_db.py.
Tu zostaje ich walidacja (422), która nie potrzebuje bazy.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

WROCLAW_GLOWNY = "1413380"

# --- /stations/nearest (walidacja, bez bazy) ----------------------------------


@pytest.mark.parametrize(
    "params",
    [
        {"lon": 17.03},
        {"lat": 51.11},
        {"lat": 91, "lon": 17.03},
        {"lat": 51.11, "lon": -181},
        {"lat": "abc", "lon": 17.03},
        {"lat": 51.11, "lon": 17.03, "limit": 0},
        {"lat": 51.11, "lon": 17.03, "limit": 51},
    ],
)
def test_nearest_rejects_invalid_params(params):
    response = client.get("/stations/nearest", params=params)

    assert response.status_code == 422
    assert "detail" in response.json()


# --- /stations/{id}/departures (walidacja, bez bazy) -------------------------


@pytest.mark.parametrize(
    "params",
    [
        {"time": "abc"},
        {"time": "08:60:00"},
        {"date": "2026-13-01"},
        {"date": "24.11.2026"},
        {"limit": 0},
        {"limit": 101},
    ],
)
def test_departures_rejects_invalid_params(params):
    response = client.get(f"/stations/{WROCLAW_GLOWNY}/departures", params=params)

    assert response.status_code == 422


# --- /segments ---------------------------------------------------------------


def test_segments_reject_invalid_date():
    response = client.get("/segments", params={"date": "jutro"})

    assert response.status_code == 422


# --- /stats (walidacja, bez bazy) ------------------------------------------


def test_stats_reject_invalid_date():
    response = client.get("/stats", params={"date": "2026-02-30"})

    assert response.status_code == 422

    