"""Testy /stations/{id}/departures na prawdziwej bazie po imporcie (#50).

Marker db (tests/conftest.py): bez bazy z importem testy są pomijane, w CI muszą przejść.
Walidacja parametrów (422) nie potrzebuje bazy i zostaje w tests/test_endpoints.py.
Wartości referencyjne: docs/decisions.md (sekcja „Wartości referencyjne do testów”).
"""

import datetime as dt

import pytest
from fastapi.testclient import TestClient

from app import db
from app.defaults import default_departures_date
from app.gtfs_time import time_to_seconds
from app.main import app

pytestmark = pytest.mark.db

client = TestClient(app)

WROCLAW_GLOWNY = "1413380"
DZIERZONIOW_SLASKI = "1413130"
REFERENCE_DAY = dt.date(2026, 11, 24)


def get_departures(station_id: str, **params) -> dict:
    response = client.get(f"/stations/{station_id}/departures", params=params)
    assert response.status_code == 200
    return response.json()


# --- zapytania w db.py ---------------------------------------------------------


def test_wroclaw_departures_count_on_reference_day():
    # Bez limitu (endpoint ma maksymalnie 100); 253 z docs/decisions.md
    departures = db.station_departures(WROCLAW_GLOWNY, REFERENCE_DAY, 0, None)

    assert len(departures) == 253


def test_line_falls_back_to_long_name():
    # Linia D8/D4/D91 ma tylko route_long_name
    lines = [
        d["line"] for d in db.station_departures(WROCLAW_GLOWNY, REFERENCE_DAY, 0, None)
    ]

    assert "D8/D4/D91" in lines
    assert all(lines)


def test_feed_range_comes_from_calendar():
    assert db.feed_range() == (dt.date(2026, 10, 19), dt.date(2026, 12, 12))


# --- endpoint ------------------------------------------------------------------


def test_departures_returns_station_and_used_date():
    body = get_departures(WROCLAW_GLOWNY, date="2026-11-24", time="08:00:00")

    assert body["station"] == {"id": WROCLAW_GLOWNY, "name": "Wrocław Główny"}
    assert body["date"] == "2026-11-24"


def test_departures_first_after_given_time():
    first = get_departures(WROCLAW_GLOWNY, date="2026-11-24", time="08:00:00")[
        "departures"
    ][0]

    assert first == {
        "departure_time": "08:07:00",
        "line": "D9/D3",
        "headsign": "Rawicz",
        "trip_id": "51385442_452555",
    }


def test_departures_are_sorted_and_not_before_time():
    departures = get_departures(
        WROCLAW_GLOWNY, date="2026-11-24", time="08:00:00", limit=100
    )["departures"]

    seconds = [time_to_seconds(d["departure_time"]) for d in departures]
    assert len(departures) == 100
    assert seconds == sorted(seconds)
    assert seconds[0] >= 8 * 3600


def test_departures_after_midnight_come_last():
    departures = get_departures(
        DZIERZONIOW_SLASKI, date="2026-11-24", time="23:00:00"
    )["departures"]

    assert [d["departure_time"] for d in departures] == [
        "23:04:00",
        "23:25:00",
        "24:12:00",
    ]


def test_departures_respects_limit():
    departures = get_departures(
        WROCLAW_GLOWNY, date="2026-11-24", time="00:00:00", limit=1
    )["departures"]

    assert len(departures) == 1


def test_departures_default_date_uses_feed_range():
    body = get_departures(WROCLAW_GLOWNY, time="00:00:00")

    assert body["date"] == default_departures_date(*db.feed_range()).isoformat()


def test_departures_outside_feed_are_empty():
    body = get_departures(WROCLAW_GLOWNY, date="2027-01-15")

    assert body["date"] == "2027-01-15"
    assert body["departures"] == []


def test_departures_unknown_station_returns_404():
    response = client.get("/stations/0/departures")

    assert response.status_code == 404
    assert "detail" in response.json()
