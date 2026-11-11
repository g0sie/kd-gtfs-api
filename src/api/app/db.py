"""Połączenie API z bazą PostGIS.

Adres bazy pochodzi ze zmiennej środowiskowej DATABASE_URL: lokalnie z pliku .env
(host 127.0.0.1), w kontenerze z docker-compose.yml (host db). W kodzie nie ma haseł.
"""

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
