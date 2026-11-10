"""Testy endpointów na danych przykładowych (zgodność z docs/api-contract.md)."""

import pytest
from fastapi.testclient import TestClient

from app.defaults import default_departures_date
from app.main import app

client = TestClient(app)

WROCLAW_GLOWNY = "1413380"
GORLITZ = "1413142"

# --- /stations ---------------------------------------------------------------


def test_stations_returns_feature_collection_of_points():
    response = client.get("/stations")

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "FeatureCollection"
    assert len(body["features"]) > 0
    for feature in body["features"]:
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


# --- /stations/nearest -------------------------------------------------------


def test_nearest_is_sorted_by_distance_and_respects_limit():
    response = client.get("/stations/nearest", params={"lat": 51.11, "lon": 17.03, "limit": 3})

    assert response.status_code == 200
    features = response.json()["features"]
    assert len(features) == 3
    distances = [f["properties"]["distance_m"] for f in features]
    assert distances == sorted(distances)
    assert features[0]["properties"]["id"] == WROCLAW_GLOWNY


def test_nearest_distance_is_rounded_to_meters():
    features = client.get("/stations/nearest", params={"lat": 51.11, "lon": 17.03}).json()[
        "features"
    ]

    for feature in features:
        distance = feature["properties"]["distance_m"]
        assert distance == round(distance)


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


# --- /stations/{id}/departures -----------------------------------------------


def test_departures_returns_station_and_used_date():
    response = client.get(
        f"/stations/{WROCLAW_GLOWNY}/departures",
        params={"date": "2026-11-24", "time": "08:00:00"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["station"] == {"id": WROCLAW_GLOWNY, "name": "Wrocław Główny"}
    assert body["date"] == "2026-11-24"


# Zależy od danych przykładowych (4 odjazdy z Wrocławia Głównego). Na bazie (#21)
# 10 odjazdów od 08:00 skończy się dużo wcześniej, więc sprawdzać np. z
# time=23:00:00 i dużym limit.
def test_departures_after_midnight_come_last():
    departures = client.get(
        f"/stations/{WROCLAW_GLOWNY}/departures",
        params={"date": "2026-11-24", "time": "08:00:00"},
    ).json()["departures"]

    times = [d["departure_time"] for d in departures]
    assert times[-1] == "24:48:00"
    assert all(t >= "08:00:00" for t in times)



# Zależy od próbki: szuka konkretnej linii D91/D64. Na bazie (#21) sprawdzać ogólnie:
# gdy route_short_name jest pusty, line == route_long_name (24.11 to D8/D4/D91).
def test_departures_line_falls_back_to_long_name():
    departures = client.get(
        f"/stations/{WROCLAW_GLOWNY}/departures",
        params={"date": "2026-11-24", "time": "00:00:00", "limit": 100},
    ).json()["departures"]

    lines = [d["line"] for d in departures]
    assert "D91/D64" in lines
    assert all(lines)


def test_departures_respects_limit():
    departures = client.get(
        f"/stations/{WROCLAW_GLOWNY}/departures",
        params={"time": "00:00:00", "limit": 1},
    ).json()["departures"]

    assert len(departures) == 1


def test_departures_default_date_matches_default_departures_date():
    body = client.get(
        f"/stations/{WROCLAW_GLOWNY}/departures", params={"time": "00:00:00"}
    ).json()

    assert body["date"] == default_departures_date().isoformat()


def test_departures_unknown_station_returns_404():
    response = client.get("/stations/0/departures")

    assert response.status_code == 404
    assert "detail" in response.json()


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


def test_segments_default_date_is_reference_day():
    response = client.get("/segments")

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "FeatureCollection"
    assert body["date"] == "2026-11-24"


def test_segments_are_line_strings_with_trip_counts():
    features = client.get("/segments", params={"date": "2026-11-22"}).json()["features"]

    assert len(features) > 0
    for feature in features:
        assert feature["geometry"]["type"] == "LineString"
        assert len(feature["geometry"]["coordinates"]) == 2
        properties = feature["properties"]
        assert isinstance(properties["from_station_id"], str)
        assert isinstance(properties["to_station_id"], str)
        assert properties["trips_per_day"] >= 0


def test_segments_echo_requested_date():
    body = client.get("/segments", params={"date": "2026-11-22"}).json()

    assert body["date"] == "2026-11-22"


def test_segments_reject_invalid_date():
    response = client.get("/segments", params={"date": "jutro"})

    assert response.status_code == 422


# --- /stats ------------------------------------------------------------------


def test_stats_default_date_and_counts():
    response = client.get("/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["date"] == "2026-11-24"
    assert body["stations_count"] > 0
    assert body["trips_count"] > 0


def test_stats_echo_requested_date():
    body = client.get("/stats", params={"date": "2026-11-22"}).json()

    assert body["date"] == "2026-11-22"


def test_stats_departures_by_hour_has_25_buckets():
    buckets = client.get("/stats").json()["departures_by_hour"]

    assert [b["hour"] for b in buckets] == list(range(25))
    assert all(b["departures"] >= 0 for b in buckets)


def test_stats_top_stations_sorted_descending():
    top = client.get("/stats").json()["top_stations"]

    assert len(top) <= 10
    counts = [s["departures_per_day"] for s in top]
    assert counts == sorted(counts, reverse=True)


def test_stats_reject_invalid_date():
    response = client.get("/stats", params={"date": "2026-02-30"})

    assert response.status_code == 422
