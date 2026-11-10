import datetime as dt
from zoneinfo import ZoneInfo

LOCAL_TIMEZONE = ZoneInfo("Europe/Warsaw")

# Dzień wzorcowy roboczy (docs/reference-day.md).
REFERENCE_DATE = dt.date(2026, 11, 24)

# Zakres obowiązywania feedu. FEED_END jest z kontraktu (2026-12-12);
# FEED_START ustaw na pierwszy dzień obowiązywania feedu z GTFS.
FEED_START = dt.date(2026, 10, 19)
FEED_END = dt.date(2026, 12, 12)


def default_departures_date() -> dt.date:
    """Dzisiaj, a gdy poza zakresem feedu - dzień wzorcowy."""
    today = dt.datetime.now(LOCAL_TIMEZONE).date()
    if FEED_START <= today <= FEED_END:
        return today
    return REFERENCE_DATE