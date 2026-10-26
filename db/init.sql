-- Schemat bazy dla rozkładu GTFS Kolei Dolnośląskich.
-- Uruchamiany automatycznie przez obraz postgis/postgis tylko przy PUSTYM wolumenie,
-- więc po zmianie tego pliku trzeba zrobić: docker compose down -v && docker compose up -d.
-- Tabele wypełnia skrypt importu (db/import_gtfs.py).

CREATE EXTENSION IF NOT EXISTS postgis;

-- Stacje (wiersze stops.txt z location_type = 1). To je pokazujemy na mapie i w API.
--   station_id   stop_id stacji z GTFS (tekst, np. '1413380')
--   is_domestic  false dla 56 stacji w Niemczech i Czechach (lista w docs/data-quality.md)
--   geom         punkt w WGS 84 (SRID 4326), kolejność współrzędnych [lon, lat]
CREATE TABLE stations (
    station_id   TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    is_domestic  BOOLEAN NOT NULL,
    geom         geometry(Point, 4326) NOT NULL
);

-- Perony (wiersze stops.txt z location_type = 0). Rozkład odwołuje się do peronów,
-- a każdy peron należy do jednej stacji (parent_station w GTFS).
CREATE TABLE platforms (
    stop_id     TEXT PRIMARY KEY,
    station_id  TEXT NOT NULL REFERENCES stations (station_id),
    name        TEXT,
    geom        geometry(Point, 4326) NOT NULL
);

-- Linie (routes.txt), np. D1. Część linii ma tylko long_name (np. 'D91/D64').
CREATE TABLE routes (
    route_id    TEXT PRIMARY KEY,
    short_name  TEXT,
    long_name   TEXT
);

-- Kursy (trips.txt). service_id wskazuje, w które dni kurs jedzie (patrz service_dates);
-- w tych danych każdy kurs ma własny service_id. headsign to kierunek kursu.
CREATE TABLE trips (
    trip_id     TEXT PRIMARY KEY,
    route_id    TEXT NOT NULL REFERENCES routes (route_id),
    service_id  TEXT NOT NULL,
    headsign    TEXT
);

-- Dni kursowania: calendar.txt rozpisany na konkretne daty z wyjątkami z calendar_dates.txt
-- (reguła w docs/reference-day.md). Jeden wiersz = "ten service_id jedzie tego dnia".
CREATE TABLE service_dates (
    service_id    TEXT NOT NULL,
    service_date  DATE NOT NULL,
    PRIMARY KEY (service_id, service_date)
);

-- Rozkład (stop_times.txt): kolejne postoje każdego kursu.
--   station_id                 stacja peronu, dodana przy imporcie, żeby odjazdy ze stacji
--                              nie wymagały łączenia z platforms
--   arrival_sec, departure_sec sekundy od północy dnia kursu; GTFS dopuszcza czasy powyżej
--                              24:00:00 (np. 24:48:00 = 89280), więc typ TIME by nie wystarczył
CREATE TABLE stop_times (
    trip_id        TEXT NOT NULL REFERENCES trips (trip_id) ON DELETE CASCADE,
    stop_sequence  INTEGER NOT NULL,
    stop_id        TEXT NOT NULL REFERENCES platforms (stop_id),
    station_id     TEXT NOT NULL REFERENCES stations (station_id),
    arrival_sec    INTEGER,
    departure_sec  INTEGER,
    PRIMARY KEY (trip_id, stop_sequence)
);

-- Indeksy przestrzenne pod wyszukiwanie najbliższych stacji
CREATE INDEX stations_geom_gix ON stations USING GIST (geom);
CREATE INDEX platforms_geom_gix ON platforms USING GIST (geom);

-- Indeksy pod zapytania API. Wyszukiwanie po trip_id obsługuje klucz główny stop_times.
CREATE INDEX stop_times_stop_idx ON stop_times (stop_id);
CREATE INDEX stop_times_station_dep_idx ON stop_times (station_id, departure_sec);
CREATE INDEX trips_service_idx ON trips (service_id);
CREATE INDEX service_dates_date_idx ON service_dates (service_date);