"""Testy funkcji trips_on_date (liczby kursów z docs/reference-day.md)."""

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


# Liczby kursów z docs/reference-day.md
@pytest.mark.parametrize(
    ("service_day", "expected_trips"),
    [
        (dt.date(2026, 11, 24), 747),  # dzień wzorcowy roboczy
        (dt.date(2026, 11, 22), 617),  # dzień wzorcowy weekendowy
        (dt.date(2026, 11, 21), 618),  # sobota
        (dt.date(2026, 11, 11), 620),  # święto
        (dt.date(2026, 10, 28), 763),  # wyjątki dodające i usuwające kursy
        (dt.date(2026, 10, 25), 629),  # kursy okresowe 25-28.10
        (dt.date(2026, 11, 12), 748),  # dodany kurs poniedziałkowy
        (dt.date(2026, 11, 17), 751),  # drobne podmiany kursów
    ],
)
def test_trips_on_date_matches_reference_day(service_day, expected_trips):
    assert query_value(COUNT_QUERY, (service_day,)) == expected_trips


def test_trips_on_date_has_no_duplicates():
    day = (dt.date(2026, 11, 24),)
    assert query_value(COUNT_QUERY, day) == query_value(DISTINCT_QUERY, day)


def test_trips_on_date_outside_feed_is_empty():
    # Feed jest ważny do 2026-12-12, później nie jedzie żaden kurs
    assert query_value(COUNT_QUERY, (dt.date(2027, 1, 15),)) == 0