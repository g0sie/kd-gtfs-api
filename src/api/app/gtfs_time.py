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


def seconds_to_time(value: int) -> str:
    """Zamienia sekundy od północy doby kursu na `HH:MM:SS`.

    Bez `% 24`, żeby kursy po północy zostały rozpoznawalne: 89280 -> "24:48:00".
    """
    if value < 0:
        raise ValueError(f"Czas nie może być ujemny: {value}")
    hours, rest = divmod(value, 3600)
    minutes, seconds = divmod(rest, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
