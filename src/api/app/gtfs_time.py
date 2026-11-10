"""Obsługa czasów GTFS, które mogą przekraczać 24:00:00 (kursy po północy)."""

import re

TIME_PATTERN = r"^\d{1,2}:[0-5]\d:[0-5]\d$"
_TIME_REGEX = re.compile(TIME_PATTERN)


def time_to_seconds(value: str) -> int:
    """Zamienia `HH:MM:SS` (także z godziną >= 24) na sekundy od północy."""
    if not _TIME_REGEX.match(value):
        raise ValueError(f"Niepoprawny format czasu: {value}")
    hours, minutes, seconds = (int(part) for part in value.split(":"))
    return hours * 3600 + minutes * 60 + seconds
