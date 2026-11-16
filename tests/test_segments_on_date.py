"""Testy funkcji segments_on_date i tabeli hop_segments.

Wartości kontrolne pochodzą z docs/segments.md (dzień wzorcowy 2026-11-24).
"""

import datetime as dt
import os

import psycopg
import pytest

pytestmark = pytest.mark.db

REFERENCE_DAY = dt.date(2026, 11, 24)
SUNDAY = dt.date(2026, 11, 22)
OUTSIDE_FEED = dt.date(2027, 1, 1)


def query_value(query: str, params: tuple = ()):
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        row = conn.execute(query, params).fetchone()
    return row[0] if row else None


def segment_trips(first_name: str, second_name: str):
    """Kursy na odcinku między dwiema stacjami (nazwy w dowolnej kolejności)."""
    return query_value(
        "SELECT trips_per_day FROM segments_on_date(%s) "
        "WHERE (from_station_name, to_station_name) IN ((%s, %s), (%s, %s))",
        (REFERENCE_DAY, first_name, second_name, second_name, first_name),
    )


def test_segment_count_on_reference_day():
    query = "SELECT count(*) FROM segments_on_date(%s)"
    assert query_value(query, (REFERENCE_DAY,)) == 327


def test_total_trips_after_splitting_express_trips():
    query = "SELECT sum(trips_per_day) FROM segments_on_date(%s)"
    assert query_value(query, (REFERENCE_DAY,)) == 10871


def test_segments_are_undirected():
    query = (
        "SELECT count(*) FROM segments_on_date(%s) "
        "WHERE from_station_id >= to_station_id"
    )
    assert query_value(query, (REFERENCE_DAY,)) == 0


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
def test_trips_on_selected_segments(first_name, second_name, trips):
    assert segment_trips(first_name, second_name) == trips


def test_express_trips_are_split_into_local_segments():
    # Strzelin – Wrocław Główny to tylko przejazd kursów przyspieszonych
    assert segment_trips("Strzelin", "Wrocław Główny") is None


def test_every_hop_has_local_segments():
    query = """
        SELECT count(*)
        FROM (
            SELECT station_id AS hop_from,
                   LEAD(station_id) OVER (
                       PARTITION BY trip_id ORDER BY stop_sequence
                   ) AS hop_to
            FROM stop_times
        ) AS h
        WHERE h.hop_to IS NOT NULL
          AND h.hop_to <> h.hop_from
          AND NOT EXISTS (
              SELECT 1 FROM hop_segments AS hs
              WHERE hs.hop_from = h.hop_from AND hs.hop_to = h.hop_to
          )
    """
    assert query_value(query) == 0


def test_segment_geometry_is_two_point_line():
    query = (
        "SELECT count(*) FROM segments_on_date(%s) "
        "WHERE GeometryType(geom) <> 'LINESTRING' "
        "OR ST_NPoints(geom) <> 2 OR ST_SRID(geom) <> 4326"
    )
    assert query_value(query, (REFERENCE_DAY,)) == 0


def test_sunday_includes_weekend_border_segments():
    query = "SELECT count(*) FROM segments_on_date(%s)"
    assert query_value(query, (SUNDAY,)) == 329


def test_date_outside_feed_is_empty():
    query = "SELECT count(*) FROM segments_on_date(%s)"
    assert query_value(query, (OUTSIDE_FEED,)) == 0