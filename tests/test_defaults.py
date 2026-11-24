"""Testy domyślnej daty odjazdów (bez bazy: zakres feedu podajemy wprost)."""

import datetime as dt

import pytest

from app.defaults import REFERENCE_DATE, default_departures_date

# Zakres feedu z data/gtfs/calendar.txt (to samo zwraca db.feed_range())
FEED_START = dt.date(2026, 10, 19)
FEED_END = dt.date(2026, 12, 12)


@pytest.mark.parametrize(
    "today", [FEED_START, dt.date(2026, 11, 16), FEED_END]
)
def test_today_inside_feed_is_used(today):
    assert default_departures_date(FEED_START, FEED_END, today=today) == today


@pytest.mark.parametrize(
    "today", [dt.date(2026, 10, 18), dt.date(2026, 12, 13), dt.date(2027, 1, 15)]
)
def test_today_outside_feed_falls_back_to_reference_day(today):
    assert default_departures_date(FEED_START, FEED_END, today=today) == REFERENCE_DATE
