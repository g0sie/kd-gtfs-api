"""Testy funkcji trips_on_date.

Liczby kursów dla dni z docs/reference-day.md sprawdza
test_reference_day_trip_counts w tests/test_import_gtfs.py (przez tę funkcję).
"""

import datetime as dt
import os

import psycopg
import pytest
from dotenv import load_dotenv

load_dotenv()
pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"), reason="brak bazy danych"
)

COUNT_QUERY = "SELECT count(*) FROM trips_on_date(%s)"
DISTINCT_QUERY = "SELECT count(DISTINCT trip_id) FROM trips_on_date(%s)"


def query_value(query: str, params: tuple = ()):
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        return conn.execute(query, params).fetchone()[0]


def test_trips_on_date_has_no_duplicates():
    day = (dt.date(2026, 11, 24),)
    assert query_value(COUNT_QUERY, day) == query_value(DISTINCT_QUERY, day)


def test_trips_on_date_outside_feed_is_empty():
    # Feed jest ważny do 2026-12-12, później nie jedzie żaden kurs
    assert query_value(COUNT_QUERY, (dt.date(2027, 1, 15),)) == 0