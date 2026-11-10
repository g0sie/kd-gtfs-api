import csv
import os
from pathlib import Path

import psycopg
import pytest
from dotenv import load_dotenv

load_dotenv()
pytestmark = pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="brak bazy danych")

GTFS_DIR = Path("data/gtfs")


def query_value(query: str, params: tuple = ()):
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        return conn.execute(query, params).fetchone()[0]


def count_file_rows(name: str) -> int:
    with (GTFS_DIR / name).open(encoding="utf-8-sig", newline="") as file:
        return sum(1 for _ in csv.DictReader(file))


@pytest.mark.skipif(not GTFS_DIR.exists(), reason="brak plików GTFS w data/gtfs")
@pytest.mark.parametrize(
    ("file_name", "query"),
    [
        ("stops.txt", "SELECT (SELECT count(*) FROM stations) + (SELECT count(*) FROM platforms)"),
        ("routes.txt", "SELECT count(*) FROM routes"),
        ("trips.txt", "SELECT count(*) FROM trips"),
        ("stop_times.txt", "SELECT count(*) FROM stop_times"),
        ("calendar_dates.txt", "SELECT count(*) FROM raw_calendar_dates"),
    ],
    ids=["stops", "routes", "trips", "stop_times", "calendar_dates"],
)
def test_tables_match_gtfs_files(file_name, query):
    assert query_value(query) == count_file_rows(file_name)


def test_time_after_midnight_is_converted():
    assert query_value("SELECT gtfs_time_to_seconds('25:13:00')") == 25 * 3600 + 13 * 60


def test_empty_time_is_null():
    assert query_value("SELECT gtfs_time_to_seconds('')") is None


def test_all_stations_imported():
    raw = query_value("SELECT count(*) FROM raw_stops WHERE location_type = '1'")
    assert query_value("SELECT count(*) FROM stations") == raw


def test_foreign_stations_marked():
    assert query_value("SELECT count(*) FROM stations WHERE NOT is_domestic") == 56


def test_every_foreign_station_from_list_exists():
    matched = query_value(
        "SELECT count(*) FROM raw_foreign_stations f "
        "JOIN stations s ON s.station_id = f.stop_id"
    )
    assert matched == query_value("SELECT count(*) FROM raw_foreign_stations")


@pytest.mark.parametrize(
    ("name", "expected_domestic"),
    [("Wrocław Główny", True), ("Zgorzelec", True), ("Görlitz", False), ("Harrachov", False)],
)
def test_is_domestic_for_selected_stations(name, expected_domestic):
    assert query_value("SELECT is_domestic FROM stations WHERE name = %s", (name,)) is expected_domestic


def test_no_platforms_lost():
    lost = query_value(
        "SELECT count(*) FROM raw_stops "
        "WHERE COALESCE(NULLIF(location_type, ''), '0') = '0' "
        "AND stop_id NOT IN (SELECT stop_id FROM platforms)"
    )
    assert lost == 0


def test_coordinates_are_lon_lat():
    lon = query_value("SELECT ST_X(geom) FROM stations WHERE name = 'Wrocław Główny'")
    lat = query_value("SELECT ST_Y(geom) FROM stations WHERE name = 'Wrocław Główny'")
    assert 16 < lon < 18
    assert 50 < lat < 52


def test_all_routes_imported():
    raw = query_value("SELECT count(*) FROM raw_routes")
    assert query_value("SELECT count(*) FROM routes") == raw


def test_empty_route_short_names_are_null():
    assert query_value("SELECT count(*) FROM routes WHERE short_name = ''") == 0
    assert query_value("SELECT count(*) FROM routes WHERE short_name IS NULL") == 7


def test_all_trips_imported():
    assert query_value("SELECT count(*) FROM trips") == 1838


def test_all_calendar_exceptions_imported():
    assert query_value("SELECT count(*) FROM raw_calendar_dates") == 1056


def test_every_trip_has_service_dates():
    without_dates = query_value(
        "SELECT count(*) FROM trips "
        "WHERE service_id NOT IN (SELECT service_id FROM service_dates)"
    )
    assert without_dates == 0


def test_all_stop_times_imported():
    raw = query_value("SELECT count(*) FROM raw_stop_times")
    assert query_value("SELECT count(*) FROM stop_times") == raw


def test_only_last_stop_has_no_pickup():
    assert query_value("SELECT count(*) FROM stop_times WHERE pickup_type = 1") == 1838
    assert query_value("SELECT count(*) FROM stop_times WHERE pickup_type <> 1") == 24753


def test_no_missing_departure_times():
    assert query_value("SELECT count(*) FROM stop_times WHERE departure_sec IS NULL") == 0


def test_times_after_midnight_are_kept():
    after_midnight = query_value("SELECT count(*) FROM stop_times WHERE departure_sec >= 86400")
    assert after_midnight == 178


@pytest.mark.parametrize(
    ("service_date", "expected_trips"),
    [
        ("2026-11-24", 747),  # dzień wzorcowy roboczy
        ("2026-11-22", 617),  # dzień wzorcowy weekendowy
        ("2026-11-21", 618),  # sobota
        ("2026-11-11", 620),  # święto: wyjątki zamieniają rozkład roboczy na świąteczny
        ("2026-10-28", 763),  # wyjątki dodające i usuwające kursy
        ("2026-10-25", 629),  # kursy okresowe 25-28.10
        ("2026-11-12", 748),  # dodany kurs poniedziałkowy
        ("2026-11-17", 751),  # drobne podmiany kursów
    ],
)
def test_reference_day_trip_counts(service_date, expected_trips):
    trips = query_value(
        "SELECT count(DISTINCT t.trip_id) FROM trips t "
        "JOIN service_dates s ON s.service_id = t.service_id "
        "WHERE s.service_date = %s",
        (service_date,),
    )
    assert trips == expected_trips