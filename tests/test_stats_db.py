
"""Testy /stats na prawdziwej bazie po imporcie (#51).

Marker db (tests/conftest.py): bez bazy z importem testy są pomijane, w CI muszą przejść.
Walidacja daty (422) nie potrzebuje bazy i zostaje w tests/test_endpoints.py.
Wartości referencyjne: docs/decisions.md (sekcja „Wartości referencyjne do testów”).
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.db

client = TestClient(app)

WROCLAW_GLOWNY = "1413380"

# Dzień: (kursy, odjazdy w całej dobie, hour: 0, hour: 24, odjazdy z Wrocławia Głównego)
REFERENCE_VALUES = {
    "2026-11-24": (747, 9551, 0, 48, 253),
    "2026-11-22": (617, 8062, 12, 48, 190),
}


def get_stats(**params) -> dict:
    response = client.get("/stats", params=params)
    assert response.status_code == 200
    return response.json()


def test_stats_default_date_is_reference_day():
    body = get_stats()

    assert body["date"] == "2026-11-24"
    assert body["trips_count"] == 747


@pytest.mark.parametrize("day", REFERENCE_VALUES)
def test_stats_match_reference_values(day):
    trips, departures, hour_0, hour_24, wroclaw = REFERENCE_VALUES[day]
    body = get_stats(date=day)
    by_hour = {b["hour"]: b["departures"] for b in body["departures_by_hour"]}

    assert body["date"] == day
    assert body["stations_count"] == 387
    assert body["trips_count"] == trips
    assert sum(by_hour.values()) == departures
    assert by_hour[0] == hour_0
    assert by_hour[24] == hour_24
    assert body["top_stations"][0] == {
        "id": WROCLAW_GLOWNY,
        "name": "Wrocław Główny",
        "departures_per_day": wroclaw,
    }


def test_stats_departures_by_hour_has_25_buckets():
    buckets = get_stats()["departures_by_hour"]

    assert [b["hour"] for b in buckets] == list(range(25))
    assert all(b["departures"] >= 0 for b in buckets)


def test_stats_top_stations_are_ten_sorted_descending():
    top = get_stats()["top_stations"]

    counts = [s["departures_per_day"] for s in top]
    assert len(top) == 10
    assert counts == sorted(counts, reverse=True)


def test_stats_top_stations_tie_is_broken_by_station_id():
    # 24.11 Środa Śląska (1413341) i Wrocław Nowy Dwór (1413388) mają po 76 odjazdów,
    # a w rankingu jest miejsce tylko dla jednej: wygrywa mniejsze station_id.
    last = get_stats(date="2026-11-24")["top_stations"][-1]

    assert last == {"id": "1413341", "name": "Środa Śląska", "departures_per_day": 76}


def test_stats_outside_feed_are_empty():
    body = get_stats(date="2027-01-15")

    assert body["stations_count"] == 387
    assert body["trips_count"] == 0
    assert body["top_stations"] == []
    assert [b["departures"] for b in body["departures_by_hour"]] == [0] * 25