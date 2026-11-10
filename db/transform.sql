-- Przerabia surowe tabele raw_* (wczytane przez db/import_gtfs.py)
-- na tabele docelowe z db/init.sql. Można uruchamiać wielokrotnie.

-- Czas GTFS na sekundy od północy dnia kursu, np. '25:13:00' -> 90780
CREATE OR REPLACE FUNCTION gtfs_time_to_seconds(value TEXT) RETURNS INTEGER AS $$
    SELECT NULLIF(split_part(trim(value), ':', 1), '')::INTEGER * 3600
         + NULLIF(split_part(trim(value), ':', 2), '')::INTEGER * 60
         + NULLIF(split_part(trim(value), ':', 3), '')::INTEGER
$$ LANGUAGE sql IMMUTABLE;

-- Kursy jadące w podanym dniu. Reguła dnia kursowania (kalendarz bazowy + wyjątki,
-- wyjątek zawsze wygrywa) jest opisana w docs/reference-day.md; tutaj korzystamy
-- z tabeli service_dates, w której import już ją zastosował.
-- Przykład: SELECT count(*) FROM trips_on_date('2026-11-24');  -- 747 kursów
CREATE OR REPLACE FUNCTION trips_on_date(service_day DATE) RETURNS SETOF trips AS $$
    SELECT t.*
    FROM trips AS t
    JOIN service_dates AS sd ON sd.service_id = t.service_id
    WHERE sd.service_date = service_day
$$ LANGUAGE sql STABLE;

TRUNCATE stop_times, trips, service_dates, routes, platforms, stations;

-- Stacje (location_type = 1), wszystkie 1:1. Stacje z db/foreign_stations.csv
-- dostają is_domestic = false (lista z docs/data-quality.md)
INSERT INTO stations (station_id, name, is_domestic, geom)
SELECT stop_id,
       stop_name,
       stop_id NOT IN (SELECT stop_id FROM raw_foreign_stations),
       ST_SetSRID(ST_MakePoint(stop_lon::FLOAT, stop_lat::FLOAT), 4326)
FROM raw_stops
WHERE location_type = '1';

-- Perony (location_type = 0 lub puste) należące do stacji
INSERT INTO platforms (stop_id, station_id, name, geom)
SELECT stop_id,
       parent_station,
       stop_name,
       ST_SetSRID(ST_MakePoint(stop_lon::FLOAT, stop_lat::FLOAT), 4326)
FROM raw_stops
WHERE COALESCE(NULLIF(location_type, ''), '0') = '0'
  AND parent_station IN (SELECT station_id FROM stations);

-- Puste nazwy zapisujemy jako NULL, żeby API mogło użyć zwykłego COALESCE
INSERT INTO routes (route_id, short_name, long_name)
SELECT route_id, NULLIF(trim(route_short_name), ''), NULLIF(trim(route_long_name), '')
FROM raw_routes;

INSERT INTO trips (trip_id, route_id, service_id, headsign)
SELECT trip_id, route_id, service_id, NULLIF(trim(trip_headsign), '')
FROM raw_trips;

-- Dni kursowania według docs/reference-day.md: kalendarz bazowy,
-- potem usuwamy dni z exception_type = 2, a na końcu dodajemy dni z exception_type = 1
-- (wyjątek zawsze wygrywa z kalendarzem)
INSERT INTO service_dates (service_id, service_date)
(
    SELECT c.service_id, d.day::DATE
    FROM raw_calendar AS c
    CROSS JOIN generate_series(to_date(c.start_date, 'YYYYMMDD')::TIMESTAMP,
                               to_date(c.end_date, 'YYYYMMDD')::TIMESTAMP,
                               INTERVAL '1 day') AS d(day)
    WHERE (ARRAY[c.monday, c.tuesday, c.wednesday, c.thursday,
                 c.friday, c.saturday, c.sunday])[EXTRACT(ISODOW FROM d.day)::INTEGER] = '1'
    EXCEPT
    SELECT service_id, to_date("date", 'YYYYMMDD')
    FROM raw_calendar_dates
    WHERE exception_type = '2'
)
UNION
SELECT service_id, to_date("date", 'YYYYMMDD')
FROM raw_calendar_dates
WHERE exception_type = '1';

-- Rozkład: każdy wpis dostaje stację swojego peronu, czasy zamienione na sekundy
INSERT INTO stop_times (trip_id, stop_sequence, stop_id, station_id, arrival_sec, departure_sec,
                        pickup_type)
SELECT st.trip_id,
       st.stop_sequence::INTEGER,
       st.stop_id,
       p.station_id,
       gtfs_time_to_seconds(st.arrival_time),
       gtfs_time_to_seconds(st.departure_time),
       COALESCE(NULLIF(trim(st.pickup_type), ''), '0')::SMALLINT
FROM raw_stop_times AS st
JOIN platforms AS p ON p.stop_id = st.stop_id
WHERE st.trip_id IN (SELECT trip_id FROM trips);