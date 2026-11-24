"""Testy GET /feed na prawdziwej bazie po imporcie (#89).

Marker db (tests/conftest.py): bez bazy z importem testy są pomijane, w CI muszą przejść.
Zakres z data/gtfs/calendar.txt: najwcześniejsze start_date i najpóźniejsze end_date.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.db

client = TestClient(app)


def test_feed_returns_range_from_calendar():
    response = client.get("/feed")

    assert response.status_code == 200
    assert response.json() == {"start_date": "2026-10-19", "end_date": "2026-12-12"}


def test_feed_range_contains_reference_days():
    body = client.get("/feed").json()

    # Dni wzorcowe (docs/reference-day.md) muszą leżeć w zakresie rozkładu
    for day in ["2026-11-22", "2026-11-24"]:
        assert body["start_date"] <= day <= body["end_date"]
