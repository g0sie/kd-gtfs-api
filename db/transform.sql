-- Przerabia surowe tabele raw_* (wczytane przez db/import_gtfs.py)
-- na tabele docelowe z db/init.sql. Można uruchamiać wielokrotnie.
-- Na końcu liczy tabelę pomocniczą hop_segments i funkcję segments_on_date
-- (odcinki sieci, docs/segments.md), bo obie potrzebują wczytanych stop_times.

-- Czas GTFS na sekundy od północy dnia kursu, np. '25:13:00' -> 90780
CREATE OR REPLACE FUNCTION gtfs_time_to_seconds(value TEXT) RETURNS INTEGER AS $$
    SELECT NULLIF(split_part(trim(value), ':', 1), '')::INTEGER * 3600
         + NULLIF(split_part(trim(value), ':', 2), '')::INTEGER * 60
         + NULLIF(split_part(trim(value), ':', 3), '')::INTEGER
$$ LANGUAGE sql IMMUTABLE;

-- Funkcja powstaje przy imporcie (python -m db.import_gtfs), nie w init.sql.
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

-- Mapowanie przejazdów na odcinki lokalne (docs/segments.md).
-- Dla każdej pary kolejnych postojów A→B z dowolnego kursu: odcinki lokalne
-- kursu wzorcowego, czyli kursu zatrzymującego się w A i B z największą
-- liczbą postojów pomiędzy. Nie zależy od daty, więc liczone raz przy imporcie.
-- Odcinki są nieskierowane: from_station_id < to_station_id.
DROP TABLE IF EXISTS hop_segments;
CREATE TABLE hop_segments AS
WITH all_stops AS (
    SELECT trip_id, station_id,
           ROW_NUMBER() OVER w AS pos,
           LEAD(station_id) OVER w AS next_station_id
    FROM stop_times
    WINDOW w AS (PARTITION BY trip_id ORDER BY stop_sequence)
),
hop_pairs AS (
    SELECT DISTINCT station_id AS hop_from, next_station_id AS hop_to
    FROM all_stops
    WHERE next_station_id IS NOT NULL
      AND next_station_id <> station_id
),
reference AS (
    SELECT DISTINCT ON (hp.hop_from, hp.hop_to)
           hp.hop_from, hp.hop_to,
           x.trip_id AS ref_trip_id,
           LEAST(x.pos, y.pos) AS pos_from,
           GREATEST(x.pos, y.pos) AS pos_to
    FROM hop_pairs AS hp
    JOIN all_stops AS x ON x.station_id = hp.hop_from
    JOIN all_stops AS y ON y.trip_id = x.trip_id AND y.station_id = hp.hop_to
    ORDER BY hp.hop_from, hp.hop_to, abs(y.pos - x.pos) DESC, x.trip_id
)
SELECT DISTINCT
       r.hop_from,
       r.hop_to,
       LEAST(s.station_id, s.next_station_id) AS from_station_id,
       GREATEST(s.station_id, s.next_station_id) AS to_station_id
FROM reference AS r
JOIN all_stops AS s
  ON s.trip_id = r.ref_trip_id
 AND s.pos >= r.pos_from
 AND s.pos < r.pos_to
WHERE s.next_station_id <> s.station_id;

ALTER TABLE hop_segments
    ADD PRIMARY KEY (hop_from, hop_to, from_station_id, to_station_id);

COMMENT ON TABLE hop_segments IS
    'Przejazd A→B (kolejne postoje kursu) → odcinki lokalne kursu wzorcowego. Tworzona przy imporcie, patrz docs/segments.md.';

-- Odcinki sieci z liczbą kursów w podanym dniu (docs/segments.md).
-- Przykład: SELECT count(*) FROM segments_on_date('2026-11-24');  -- 327
CREATE OR REPLACE FUNCTION segments_on_date(service_day DATE)
RETURNS TABLE (
    from_station_id   TEXT,
    from_station_name TEXT,
    to_station_id     TEXT,
    to_station_name   TEXT,
    trips_per_day     INTEGER,
    geom              geometry(LineString, 4326)
)
LANGUAGE sql STABLE
AS $$
    WITH day_hops AS (
        -- przejazdy między kolejnymi postojami kursów z podanego dnia
        SELECT st.trip_id,
               st.station_id AS hop_from,
               LEAD(st.station_id) OVER (
                   PARTITION BY st.trip_id ORDER BY st.stop_sequence
               ) AS hop_to
        FROM stop_times AS st
        JOIN trips_on_date(service_day) AS t ON t.trip_id = st.trip_id
    ),
    counted AS (
        -- ostatni postój (hop_to IS NULL) i pary A→A nie mają wiersza
        -- w hop_segments, więc odpadają przy złączeniu
        SELECT hs.from_station_id AS a,
               hs.to_station_id AS b,
               count(DISTINCT dh.trip_id) AS trips
        FROM day_hops AS dh
        JOIN hop_segments AS hs
          ON hs.hop_from = dh.hop_from
         AND hs.hop_to = dh.hop_to
        GROUP BY hs.from_station_id, hs.to_station_id
    )
    SELECT c.a, sa.name, c.b, sb.name, c.trips::INTEGER,
           ST_MakeLine(sa.geom, sb.geom)
    FROM counted AS c
    JOIN stations AS sa ON sa.station_id = c.a
    JOIN stations AS sb ON sb.station_id = c.b
    ORDER BY c.a, c.b
$$;
