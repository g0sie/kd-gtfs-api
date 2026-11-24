import datetime as dt
from zoneinfo import ZoneInfo

LOCAL_TIMEZONE = ZoneInfo("Europe/Warsaw")

# Dzień wzorcowy roboczy (docs/reference-day.md).
REFERENCE_DATE = dt.date(2026, 11, 24)


def default_departures_date(
    feed_start: dt.date, feed_end: dt.date, today: dt.date | None = None
) -> dt.date:
    """Dzisiaj, a gdy poza zakresem feedu - dzień wzorcowy.

    Zakres feedu pochodzi z kalendarza w bazie (db.feed_range()), a nie ze stałych,
    więc po imporcie nowego rozkładu nie trzeba zmieniać kodu (docs/decisions.md).
    Parametr today pozwala testować funkcję bez zależności od bieżącej daty.
    """
    if today is None:
        today = dt.datetime.now(LOCAL_TIMEZONE).date()
    if feed_start <= today <= feed_end:
        return today
    return REFERENCE_DATE
