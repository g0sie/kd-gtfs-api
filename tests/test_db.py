"""Testy warstwy app.db na prawdziwej bazie po imporcie (#18).

Pomijanie bez bazy albo danych: marker db z tests/conftest.py.
"""

import pytest

from app import db

pytestmark = pytest.mark.db


def test_station_count_matches_import():
    assert db.count_stations() == 387


def test_nearest_station_uses_geography_distance():
    stations = db.nearest_stations(lat=51.11, lon=17.03, limit=3)

    assert [s["id"] for s in stations][0] == "1413380"
    distances = [s["distance_m"] for s in stations]
    assert distances == sorted(distances)
    # Odległość w metrach (geography), a nie w stopniach (geometry)
    assert 1000 < distances[0] < 2000
