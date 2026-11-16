"""Połączenie API z bazą PostGIS.

Adres bazy pochodzi ze zmiennej środowiskowej DATABASE_URL: lokalnie z pliku .env
(host 127.0.0.1), w kontenerze z docker-compose.yml (host db). W kodzie nie ma haseł.
"""

import datetime as dt
import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()

# Bez limitu psycopg potrafi wisieć na połączeniu (np. localhost i IPv6 na Windowsie)
CONNECT_TIMEOUT_S = 3


class DatabaseNotConfiguredError(RuntimeError):
    """Brak zmiennej środowiskowej DATABASE_URL."""


def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise DatabaseNotConfiguredError("Brak zmiennej środowiskowej DATABASE_URL")
    return url


def connect() -> psycopg.Connection:
    return psycopg.connect(get_database_url(), connect_timeout=CONNECT_TIMEOUT_S)


def check_connection() -> str:
    """Stan połączenia dla /health: 'ok', 'unavailable' albo 'not_configured'."""
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
    except DatabaseNotConfiguredError:
        return "not_configured"
    except psycopg.Error:
        return "unavailable"
    return "ok"


def database_status() -> tuple[str, int | None]:
    """Stan bazy i liczba stacji jednym połączeniem (dla /health)."""
    try:
        with connect() as conn:
            stations_count = conn.execute("SELECT count(*) FROM stations").fetchone()[0]
    except DatabaseNotConfiguredError:
        return "not_configured", None
    except psycopg.Error:
        return "unavailable", None
    return "ok", stations_count


def count_stations() -> int:
    """Zapytanie testowe: liczba stacji (bez peronów) w zaimportowanych danych."""
    with connect() as conn:
        return conn.execute("SELECT count(*) FROM stations").fetchone()[0]


def list_stations() -> list[dict]:
    """Wszystkie stacje (bez peronów), także zagraniczne.

    Kolumny nazywają się tak samo jak w nearest_stations(), więc router buduje
    z obu wyników GeoJSON tą samą funkcją. ORDER BY daje stałą kolejność odpowiedzi.
    """
    query = """
        SELECT station_id AS id,
               name,
               is_domestic,
               ST_X(geom) AS lon,
               ST_Y(geom) AS lat
        FROM stations
        ORDER BY station_id
    """
    with connect() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query)
        return cur.fetchall()


def nearest_stations(lat: float, lon: float, limit: int = 5) -> list[dict]:
    """Najbliższe stacje do punktu.

    Kolumny geom są typu geometry(Point, 4326), czyli w stopniach, więc odległość
    liczymy po rzutowaniu na geography (metry na elipsoidzie, docs/decisions.md).
    """
    query = """
        SELECT station_id AS id,
               name,
               is_domestic,
               ST_X(geom) AS lon,
               ST_Y(geom) AS lat,
               round(ST_Distance(geom::geography, point.geog)) AS distance_m
        FROM stations,
             (SELECT ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)::geography AS geog)
                 AS point
        ORDER BY geom::geography <-> point.geog
        LIMIT %(limit)s
    """
    with connect() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, {"lat": lat, "lon": lon, "limit": limit})
        return cur.fetchall()


def get_station(station_id: str) -> dict | None:
    """Stacja o podanym identyfikatorze albo None, gdy jej nie ma."""
    query = "SELECT station_id AS id, name FROM stations WHERE station_id = %s"
    with connect() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, (station_id,))
        return cur.fetchone()


def station_departures(
    station_id: str, service_date: dt.date, start_sec: int, limit: int | None
) -> list[dict]:
    """Odjazdy ze stacji w danym dniu od podanej sekundy doby kursu.

    Kursy z dnia bierzemy z funkcji trips_on_date (#24). Warunek pickup_type <> 1
    musi być dokładnie taki, bo na nim opiera się indeks stop_times_departures_idx
    (docs/decisions.md). limit=None oznacza wszystkie odjazdy (LIMIT NULL).
    """
    query = """
        SELECT st.departure_sec,
               COALESCE(r.short_name, r.long_name) AS line,
               t.headsign,
               t.trip_id
        FROM stop_times AS st
        JOIN trips_on_date(%(service_date)s) AS t ON t.trip_id = st.trip_id
        JOIN routes AS r ON r.route_id = t.route_id
        WHERE st.station_id = %(station_id)s
          AND st.pickup_type <> 1
          AND st.departure_sec >= %(start_sec)s
        ORDER BY st.departure_sec, t.trip_id
        LIMIT %(limit)s
    """
    params = {
        "station_id": station_id,
        "service_date": service_date,
        "start_sec": start_sec,
        "limit": limit,
    }
    with connect() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, params)
        return cur.fetchall()


def feed_range() -> tuple[dt.date, dt.date]:
    """Zakres obowiązywania feedu z kalendarza w bazie.

    Najwcześniejsze start_date i najpóźniejsze end_date z calendar.txt (raw_calendar
    tworzy import, daty są tekstem YYYYMMDD).
    """
    query = """
        SELECT min(to_date(start_date, 'YYYYMMDD')),
               max(to_date(end_date, 'YYYYMMDD'))
        FROM raw_calendar
    """
    with connect() as conn:
        return conn.execute(query).fetchone()