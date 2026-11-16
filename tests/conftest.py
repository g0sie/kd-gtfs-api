"""Wspólne ustawienia testów.

Testy bazy oznaczamy markerem `db` (w pliku: `pytestmark = pytest.mark.db`,
przy pojedynczym teście: `@pytest.mark.db`). Wykonują się tylko wtedy, gdy baza
działa i import był uruchomiony; w przeciwnym razie są pomijane z jednym,
wspólnym powodem. Gdy ustawiona jest zmienna REQUIRE_DB (np. w CI), brak bazy
kończy te testy błędem zamiast pominięciem.
"""

import functools
import os

import psycopg
import pytest
from dotenv import load_dotenv

load_dotenv()

CONNECT_TIMEOUT_S = 3
HOW_TO_FIX = "docker compose up -d db, potem python -m db.import_gtfs data/gtfs"


@functools.cache
def database_problem() -> str | None:
    """Powód, dla którego testów bazy nie da się uruchomić, albo None."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return "brak DATABASE_URL"
    try:
        with psycopg.connect(database_url, connect_timeout=CONNECT_TIMEOUT_S) as conn:
            # Tabele raw_* tworzy dopiero import, a nie init.sql
            imported = conn.execute(
                "SELECT to_regclass('public.raw_stops') IS NOT NULL"
            ).fetchone()[0]
    except psycopg.Error:
        return "baza nie odpowiada"
    if not imported:
        return "import nie był uruchomiony"
    return None


def require_db() -> bool:
    return os.environ.get("REQUIRE_DB", "") not in ("", "0")


@pytest.fixture(autouse=True)
def _database_guard(request):
    """Pomija (albo przy REQUIRE_DB oblewa) testy z markerem db, gdy baza nie jest gotowa."""
    if request.node.get_closest_marker("db") is None:
        return
    problem = database_problem()
    if problem is None:
        return
    message = f"brak bazy albo danych ({problem}): {HOW_TO_FIX}"
    if require_db():
        pytest.fail(f"REQUIRE_DB jest ustawione, a {message}", pytrace=False)
    pytest.skip(message)