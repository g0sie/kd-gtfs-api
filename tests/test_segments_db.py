"""Testy /segments na prawdziwej bazie po imporcie (#54).

Marker db (tests/conftest.py): bez bazy z importem testy są pomijane, w CI muszą przejść.
Walidacja parametrów (422) nie potrzebuje bazy i zostaje w tests/test_endpoints.py.
Wartości kontrolne pochodzą z docs/segments.md.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.db

client = TestClient(app)

WROCLAW_GLOWNY = "1413380"
SEGMENT_PROPERTIES = {
    "from_station_id",
    "from_station_name",
    "to_station_id",
    "to_station_name",
    "trips_per_day",
}


def find_segment(features: list[dict], first_name: str, second_name: str) -> dict | None:
    """Odcinek między dwiema stacjami (nazwy w dowolnej kolejności)."""
    names = {first_name, second_name}
    for feature in features:
        properties = feature["properties"]
        if {properties["from_station_name"], properties["to_station_name"]} == names:
            return feature
    return None


def test_segments_default_date_is_reference_day():
    response = client.get("/segments")

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "FeatureCollection"
    assert body["date"] == "2026-11-24"
    assert len(body["features"]) == 327


def test_segments_echo_requested_date():
    body = client.get("/segments", params={"date": "2026-11-22"}).json()

    assert body["date"] == "2026-11-22"
    assert len(body["features"]) == 329


def test_segments_outside_feed_are_empty():
    body = client.get("/segments", params={"date": "2027-01-01"}).json()

    assert body["date"] == "2027-01-01"
    assert body["features"] == []


def test_segments_are_line_strings_with_contract_properties():
    features = client.get("/segments").json()["features"]

    for feature in features:
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "LineString"
        assert len(feature["geometry"]["coordinates"]) == 2
        properties = feature["properties"]
        assert set(properties) == SEGMENT_PROPERTIES
        assert properties["from_station_id"] < properties["to_station_id"]
        assert properties["trips_per_day"] > 0


def test_segments_have_stable_order():
    features = client.get("/segments").json()["features"]
    keys = [
        (f["properties"]["from_station_id"], f["properties"]["to_station_id"])
        for f in features
    ]

    assert keys == sorted(keys)


@pytest.mark.parametrize(
    ("first_name", "second_name", "trips"),
    [
        ("Wrocław Główny", "Wrocław Mikołajów", 160),
        ("Wrocław Główny", "Wrocław Muchobór", 122),
        ("Pustków Żurawski", "Wierzbice", 28),
        ("Lipinki Łużyckie", "Sieniawa Żarska", 4),
    ],
    ids=["busiest", "second", "middle", "quietest"],
)
def test_trips_per_day_on_selected_segments(first_name, second_name, trips):
    features = client.get("/segments").json()["features"]
    segment = find_segment(features, first_name, second_name)

    assert segment is not None
    assert segment["properties"]["trips_per_day"] == trips


def test_segment_coordinates_are_lon_lat():
    # Wrocław Główny: lat 51.097917, lon 17.037957 (docs/api-contract.md)
    features = client.get("/segments").json()["features"]
    segment = find_segment(features, "Wrocław Główny", "Wrocław Mikołajów")
    end = 0 if segment["properties"]["from_station_id"] == WROCLAW_GLOWNY else 1

    assert segment["geometry"]["coordinates"][end] == pytest.approx(
        [17.037957, 51.097917], abs=1e-6
    )
