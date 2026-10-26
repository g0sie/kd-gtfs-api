-- Schemat bazy dla rozkładu GTFS Kolei Dolnośląskich.
-- Uruchamiany automatycznie przez obraz postgis/postgis tylko przy PUSTYM wolumenie.

CREATE EXTENSION IF NOT EXISTS postgis;

-- Stacje (location_type = 1) - to pokazujemy na mapie.
-- is_domestic = false dla stacji w Niemczech i Czechach (lista w db/foreign_stations.csv)
CREATE TABLE stations (
    station_id   TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    is_domestic  BOOLEAN NOT NULL,
    geom         geometry(Point, 4326) NOT NULL
);

-- Perony (location_type = 0), każdy przypisany do stacji
CREATE TABLE platforms (
    stop_id     TEXT PRIMARY KEY,
    station_id  TEXT NOT NULL REFERENCES stations (station_id),
    name        TEXT,
    geom        geometry(Point, 4326) NOT NULL
);

CREATE TABLE routes (
    route_id    TEXT PRIMARY KEY,
    short_name  TEXT,
    long_name   TEXT
);

CREATE TABLE trips (
    trip_id     TEXT PRIMARY KEY,
    route_id    TEXT NOT NULL REFERENCES routes (route_id),
    service_id  TEXT NOT NULL,
    headsign    TEXT
);

-- Rozwinięte calendar.txt + calendar_dates.txt: w które dni kursuje dany service_id
CREATE TABLE service_dates (
    service_id    TEXT NOT NULL,
    service_date  DATE NOT NULL,
    PRIMARY KEY (service_id, service_date)
);

-- Czasy jako sekundy od północy dnia kursu, bo GTFS dopuszcza np. 25:13:00
CREATE TABLE stop_times (
    trip_id        TEXT NOT NULL REFERENCES trips (trip_id) ON DELETE CASCADE,
    stop_sequence  INTEGER NOT NULL,
    stop_id        TEXT NOT NULL REFERENCES platforms (stop_id),
    station_id     TEXT NOT NULL REFERENCES stations (station_id),
    arrival_sec    INTEGER,
    departure_sec  INTEGER,
    PRIMARY KEY (trip_id, stop_sequence)
);

CREATE INDEX stations_geom_gix ON stations USING GIST (geom);
CREATE INDEX platforms_geom_gix ON platforms USING GIST (geom);
-- Wyszukiwanie po trip_id obsługuje klucz główny (trip_id, stop_sequence)
CREATE INDEX stop_times_stop_idx ON stop_times (stop_id);
CREATE INDEX stop_times_station_dep_idx ON stop_times (station_id, departure_sec);
CREATE INDEX trips_service_idx ON trips (service_id);
CREATE INDEX service_dates_date_idx ON service_dates (service_date);