"""Import rozkładu GTFS Kolei Dolnośląskich do PostGIS.

Krok 1: każdy plik GTFS trafia bez zmian do tabeli raw_<nazwa> (wszystkie kolumny jako tekst).
Krok 2: db/transform.sql przerabia tabele raw_* na tabele docelowe z db/init.sql.

Użycie (z głównego folderu projektu):
    python -m db.import_gtfs data/gtfs
"""

import csv
import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg import sql

GTFS_FILES = ["stops", "routes", "trips", "stop_times", "calendar", "calendar_dates"]
FOREIGN_STATIONS_FILE = Path("db/foreign_stations.csv")
TRANSFORM_SQL_FILE = Path("db/transform.sql")

# Kolumny plików kalendarza na wypadek, gdyby któregoś nie było w paczce GTFS
OPTIONAL_FILE_COLUMNS = {
    "calendar": ["service_id", "monday", "tuesday", "wednesday", "thursday",
                 "friday", "saturday", "sunday", "start_date", "end_date"],
    "calendar_dates": ["service_id", "date", "exception_type"],
}


def read_header(path: Path) -> list[str]:
    with path.open(encoding="utf-8-sig", newline="") as file:
        return [column.strip() for column in next(csv.reader(file))]


def create_raw_table(cur: psycopg.Cursor, table: str, columns: list[str]) -> None:
    cur.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table)))
    column_defs = sql.SQL(", ").join(
        sql.SQL("{} TEXT").format(sql.Identifier(column)) for column in columns
    )
    cur.execute(sql.SQL("CREATE TABLE {} ({})").format(sql.Identifier(table), column_defs))


def load_raw_file(cur: psycopg.Cursor, path: Path, table: str) -> None:
    """Wczytuje plik CSV bez zmian do tabeli, w której każda kolumna jest tekstem."""
    create_raw_table(cur, table, read_header(path))
    query = sql.SQL("COPY {} FROM STDIN WITH (FORMAT csv, HEADER true)").format(
        sql.Identifier(table)
    )
    with cur.copy(query) as copy:
        copy.write(path.read_bytes())


def import_gtfs(gtfs_dir: Path, database_url: str) -> None:
    with psycopg.connect(database_url) as conn, conn.cursor() as cur:
        for name in GTFS_FILES:
            path = gtfs_dir / f"{name}.txt"
            if path.exists():
                load_raw_file(cur, path, f"raw_{name}")
            else:
                create_raw_table(cur, f"raw_{name}", OPTIONAL_FILE_COLUMNS[name])
        load_raw_file(cur, FOREIGN_STATIONS_FILE, "raw_foreign_stations")
        cur.execute(TRANSFORM_SQL_FILE.read_text(encoding="utf-8"))


def main() -> None:
    load_dotenv()
    import_gtfs(Path(sys.argv[1]), os.environ["DATABASE_URL"])


if __name__ == "__main__":
    main()