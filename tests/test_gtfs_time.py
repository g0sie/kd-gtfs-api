"""Testy zamiany czasów GTFS (nie wymagają bazy)."""

import pytest

from app.gtfs_time import seconds_to_time, time_to_seconds


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0, "00:00:00"),
        (8 * 3600 + 12 * 60, "08:12:00"),
        (86399, "23:59:59"),
        (86400, "24:00:00"),
        (89280, "24:48:00"),
        (90780, "25:13:00"),
    ],
)
def test_seconds_to_time(seconds, expected):
    assert seconds_to_time(seconds) == expected


@pytest.mark.parametrize("value", ["00:00:00", "08:12:00", "24:48:00", "25:13:00"])
def test_seconds_to_time_reverses_time_to_seconds(value):
    assert seconds_to_time(time_to_seconds(value)) == value


def test_seconds_to_time_rejects_negative():
    with pytest.raises(ValueError):
        seconds_to_time(-1)
