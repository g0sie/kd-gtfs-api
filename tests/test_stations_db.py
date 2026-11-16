"""Testy /stations i /stations/nearest na prawdziwej bazie po imporcie (#49).

Marker db (tests/conftest.py): bez bazy z importem testy są pomijane, w CI muszą przejść.
Walidacja parametrów (422) nie potrzebuje bazy i zostaje w tests/test_endpoints.py.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.db

client = TestClient(app)

WROCLAW_GLOWNY = "1413380"
GORLITZ = "1413142"

# --- /stations ---------------------------------------------------------------


def test_stations_returns_all_stations_from_database():
    response = client.get("/stations")

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "FeatureCollection"
    assert len(body["features"]) == 387


def test_stations_features_are_points_with_contract_properties():
    features = client.get("/stations").json()["features"]

    for feature in features:
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "Point"
        assert set(feature["properties"]) == {"id", "name", "is_domestic"}
        assert isinstance(feature["properties"]["id"], str)


def test_stations_coordinates_are_lon_lat():
    features = client.get("/stations").json()["features"]
    wroclaw = next(f for f in features if f["properties"]["id"] == WROCLAW_GLOWNY)

    lon, lat = wroclaw["geometry"]["coordinates"]
    assert lon == pytest.approx(17.04, abs=0.01)
    assert lat == pytest.approx(51.10, abs=0.01)


def test_stations_mark_foreign_stations():
    features = client.get("/stations").json()["features"]
    by_id = {f["properties"]["id"]: f["properties"] for f in features}

    assert by_id[WROCLAW_GLOWNY]["is_domestic"] is True
    assert by_id[GORLITZ]["is_domestic"] is False
    # 56 stacji zagranicznych (docs/data-quality.md)
    assert sum(not p["is_domestic"] for p in by_id.values()) == 56


# --- /stations/nearest -------------------------------------------------------


def test_nearest_is_sorted_by_distance_and_respects_limit():
    response = client.get(
        "/stations/nearest", params={"lat": 51.11, "lon": 17.03, "limit": 3}
    )

    assert response.status_code == 200
    features = response.json()["features"]
    assert len(features) == 3
    distances = [f["properties"]["distance_m"] for f in features]
    assert distances == sorted(distances)
    assert features[0]["properties"]["id"] == WROCLAW_GLOWNY


def test_nearest_distance_is_geography_in_meters():
    features = client.get(
        "/stations/nearest", params={"lat": 51.11, "lon": 17.03, "limit": 1}
    ).json()["features"]

    # Baza liczy na elipsoidzie (geography): 1455 m. Mock z haversine (kula) dawał 1454.
    assert features[0]["properties"]["distance_m"] == 1455


def test_nearest_distance_is_rounded_to_meters():
    features = client.get(
        "/stations/nearest", params={"lat": 51.11, "lon": 17.03}
    ).json()["features"]

    assert len(features) == 5  # domyślny limit
    for feature in features:
        distance = feature["properties"]["distance_m"]
        assert distance == round(distance)