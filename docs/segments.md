# Odcinki sieci (`/segments`)

W danych GTFS Kolei Dolnośląskich nie ma `shapes.txt`, więc odcinki sieci (linie między stacjami) budujemy sami z rozkładu. Ten dokument opisuje, jak to robimy, żeby z opisu dało się zrobić funkcję SQL w bazie i endpoint `/segments` zgodny z [api-contract.md](api-contract.md).

Sprawdzone 11.11.2026 w QGIS na zaimportowanej bazie (#18), dla dnia wzorcowego 2026-11-24 ([reference-day.md](reference-day.md)).

## Definicja odcinka

1. Bierzemy kursy aktywne w podanym dniu: `trips_on_date(service_day)` (#24).
2. Dla każdego kursu łączymy w pary **kolejne postoje** (stację postoju i stację następnego postoju). Używamy `LEAD(station_id) OVER (PARTITION BY trip_id ORDER BY stop_sequence)`, a nie `stop_sequence + 1` – w danych nie ma przerw w numeracji, ale `LEAD` działa także wtedy, gdyby się pojawiły.
3. Odrzucamy pary, w których obie stacje są takie same (dwa kolejne postoje na różnych peronach tej samej stacji). W obecnych danych nie ma takich par.
4. Stacje bierzemy z kolumny `stop_times.station_id` (#38), więc nie trzeba mapować peronów przez `parent_station`.

Dla 2026-11-24 daje to **9 551 przejazdów** między kolejnymi postojami – dokładnie tyle, ile jest odjazdów bez ostatniego przystanku kursu ([decisions.md](decisions.md), wartości referencyjne).

## Kierunek: odcinki nieskierowane

**A→B i B→A to jeden odcinek.** `trips_per_day` to suma kursów w obu kierunkach.

Uzasadnienie:

- bez `shapes.txt` odcinki A→B i B→A miałyby identyczną geometrię i na mapie nakładałyby się na siebie,
- sieć jest praktycznie symetryczna: przed rozbiciem kursów przyspieszonych (niżej) było 799 odcinków skierowanych i 402 nieskierowane, czyli tylko 5 odcinków miało kursy w jedną stronę – i wszystkie pięć to kursy przyspieszone (Międzylesie → Bystrzyca Kłodzka, Bystrzyca Kłodzka → Kłodzko Miasto, Długołęka → Oleśnica, Strzegom → Jawor, Jaworzyna Śląska → Strzegom). Po rozbiciu kursów przyspieszonych sieć jest w pełni symetryczna.

**Pola `from_station_id` i `to_station_id`:** jako `from` zawsze stacja z **mniejszym** `station_id`, jako `to` – z większym. Identyfikatory są tekstem, ale wszystkie mają tę samą długość (np. `1413380`), więc porównanie tekstowe (`LEAST` / `GREATEST`) daje tę samą kolejność co liczbowe. `from` / `to` nie oznacza więc kierunku jazdy.

## Kursy przyspieszone: rozbijamy na odcinki lokalne

Kurs, który nie zatrzymuje się na stacjach pośrednich, tworzy z definicji jeden długi odcinek, np. Strzelin – Wrocław Główny (35 km). Bez dodatkowego kroku:

- na mapie taki odcinek byłby prostą „cięciwą” nad łańcuchem odcinków lokalnych,
- odcinki lokalne nie liczyłyby kursów, które fizycznie po nich jadą, tylko się nie zatrzymują – a kontrakt definiuje `trips_per_day` jako kursy, które **przejeżdżają** odcinek.

Dla 2026-11-24 takich odcinków jest **75 z 402**, głównie na liniach wychodzących z Wrocławia (Strzelin, Oława, Środa Śląska, Brzeg Dolny, Oborniki Śląskie).

**Reguła rozbijania:**

1. Dla każdej pary kolejnych postojów A–B szukamy **kursu wzorcowego**: kursu (z dowolnego dnia), który zatrzymuje się i w A, i w B, i ma między nimi **najwięcej postojów**.
2. Przejazd A → B zastępujemy odcinkami między kolejnymi postojami kursu wzorcowego od A do B. Kurs przyspieszony „dostaje” stacje, które pominął.
3. Dla zwykłego odcinka lokalnego kursem wzorcowym jest kurs bez postojów pośrednich, więc odcinek się nie zmienia – jedna reguła działa dla wszystkich odcinków.

Kurs wzorcowy szukamy we **wszystkich** kursach, nie tylko z podanego dnia: układ torów nie zależy od daty, więc kurs przyspieszony da się rozbić także w dniu, w którym lokalny kurs na tej linii nie jeździ.

Po rozbiciu dla 2026-11-24 zostaje **327 odcinków** (402 − 75): wszystkie odcinki przyspieszone zniknęły, a rozbijanie nie utworzyło żadnego nowego odcinka – każdy kurs przyspieszony rozłożył się na odcinki, które już istnieją w sieci.

## Szkic funkcji SQL

Wzorowana na `trips_on_date` w `db/transform.sql`: parametr `service_day`, a nie `service_date`, żeby nie zderzał się z kolumną `service_dates.service_date`.

```sql
-- Odcinki sieci z liczbą kursów w podanym dniu (docs/segments.md).
-- Odcinki nieskierowane: from_station_id < to_station_id.
-- Kursy przyspieszone są rozbite na odcinki lokalne według kursu wzorcowego.
-- Przykład: SELECT count(*) FROM segments_on_date('2026-11-24');  -- 327 odcinków
CREATE OR REPLACE FUNCTION segments_on_date(service_day DATE)
RETURNS TABLE (
    from_station_id   TEXT,
    from_station_name TEXT,
    to_station_id     TEXT,
    to_station_name   TEXT,
    trips_per_day     INTEGER,
    geom              geometry(LineString, 4326)
) AS $$
    WITH all_stops AS (
        -- postoje wszystkich kursów (do wyboru kursu wzorcowego)
        SELECT trip_id, station_id,
               ROW_NUMBER() OVER w AS pos,
               LEAD(station_id) OVER w AS next_station_id
        FROM stop_times
        WINDOW w AS (PARTITION BY trip_id ORDER BY stop_sequence)
    ),
    hops AS (
        -- przejazdy między kolejnymi postojami kursów z podanego dnia
        SELECT s.trip_id, s.station_id AS a, s.next_station_id AS b
        FROM all_stops AS s
        JOIN trips_on_date(service_day) AS t ON t.trip_id = s.trip_id
        WHERE s.next_station_id IS NOT NULL
          AND s.next_station_id <> s.station_id
    ),
    hop_pairs AS (
        SELECT DISTINCT a, b FROM hops
    ),
    reference AS (
        -- kurs wzorcowy: zatrzymuje się w A i B, a między nimi ma najwięcej postojów
        SELECT DISTINCT ON (hp.a, hp.b)
               hp.a, hp.b,
               x.trip_id AS ref_trip_id,
               LEAST(x.pos, y.pos) AS pos_from,
               GREATEST(x.pos, y.pos) AS pos_to
        FROM hop_pairs AS hp
        JOIN all_stops AS x ON x.station_id = hp.a
        JOIN all_stops AS y ON y.trip_id = x.trip_id AND y.station_id = hp.b
        ORDER BY hp.a, hp.b, abs(y.pos - x.pos) DESC, x.trip_id
    ),
    local_hops AS (
        -- odcinki lokalne kursu wzorcowego między A i B (nieskierowane)
        SELECT r.a AS hop_a, r.b AS hop_b,
               LEAST(s.station_id, s.next_station_id) AS a,
               GREATEST(s.station_id, s.next_station_id) AS b
        FROM reference AS r
        JOIN all_stops AS s
          ON s.trip_id = r.ref_trip_id
         AND s.pos >= r.pos_from
         AND s.pos < r.pos_to
        WHERE s.next_station_id <> s.station_id
    ),
    expanded AS (
        SELECT h.trip_id, l.a, l.b
        FROM hops AS h
        JOIN local_hops AS l ON l.hop_a = h.a AND l.hop_b = h.b
    ),
    counted AS (
        SELECT a, b, count(DISTINCT trip_id) AS trips
        FROM expanded
        GROUP BY a, b
    )
    SELECT c.a, sa.name, c.b, sb.name, c.trips::INTEGER,
           ST_MakeLine(sa.geom, sb.geom)
    FROM counted AS c
    JOIN stations AS sa ON sa.station_id = c.a
    JOIN stations AS sb ON sb.station_id = c.b
$$ LANGUAGE sql STABLE;
```

Wynik odpowiada polom `/segments` w [api-contract.md](api-contract.md): `from_station_id`, `from_station_name`, `to_station_id`, `to_station_name`, `trips_per_day`, a `geom` to geometria `LineString` do `Feature`.

Do podglądu w QGIS (Bazy danych → Zarządzanie bazami danych → Okno SQL, „Wczytaj jako nową warstwę”) potrzebna jest kolumna z unikalnymi wartościami, np.:

```sql
SELECT from_station_id || '-' || to_station_id AS id, *
FROM segments_on_date('2026-11-24');
```

## Wartości kontrolne (2026-11-24)

| Wartość | Wynik |
|---|---|
| przejazdy między kolejnymi postojami (przed rozbiciem) | 9 551 |
| przejazdy po rozbiciu kursów przyspieszonych | 10 871 |
| odcinki przed rozbiciem (nieskierowane) | 402 |
| odcinki rozbite (przyspieszone) | 75 |
| **odcinki w wyniku** | **327** |

Wybrane odcinki:

| Odcinek | `trips_per_day` |
|---|---|
| Wrocław Główny – Wrocław Mikołajów | 160 |
| Wrocław Główny – Wrocław Muchobór | 122 |
| Wrocław Nadodrze – Wrocław Sołtysowice | 110 |
| Wrocław Mikołajów – Wrocław Szczepin | 102 |
| Wrocław Nadodrze – Wrocław Szczepin | 102 |
| Pustków Żurawski – Wierzbice: odcinek ze środka zestawienia | 28 |
| Lipinki Łużyckie – Sieniawa Żarska: odcinek z najmniejszą liczbą kursów | 4 |

   Na mapie najgrubsze odcinki tworzą promienie wychodzące z Wrocławia, a najcieńsze są na obrzeżach sieci i końcówkach linii (np. Lipinki Łużyckie – Sieniawa Żarska).

## Kontrola objazdów

Reguła „najwięcej postojów” zakłada, że kurs wzorcowy jedzie z A do B tą samą trasą co kurs przyspieszony. Gdyby jakiś kurs jechał objazdem przez inną linię, przejazdy kursu przyspieszonego zostałyby przypisane niewłaściwym odcinkom.

Sprawdzenie: dla każdego rozbitego odcinka porównujemy długość trasy przez stacje pośrednie z linią prostą A–B. Tory zakręcają, więc stosunek 1,0–1,3 jest normalny; wartości powyżej ok. 1,5 oznaczałyby objazd.

Wynik dla 2026-11-24: największy stosunek to **1,41** (Piechowice – Szklarska Poręba Dolna: 2 km w linii prostej, 3 km po trasie – krótki, kręty odcinek górski), kolejne to 1,27 (Długołęka – Oleśnica Rataje) i 1,17. **Objazdów nie znaleziono.** Kontrolę warto powtórzyć po każdej zmianie danych GTFS:

```sql
WITH all_stops AS (
    SELECT trip_id, station_id,
           ROW_NUMBER() OVER w AS pos,
           LEAD(station_id) OVER w AS next_station_id
    FROM stop_times
    WINDOW w AS (PARTITION BY trip_id ORDER BY stop_sequence)
),
day_stops AS (
    SELECT s.*
    FROM all_stops AS s
    JOIN trips_on_date(DATE '2026-11-24') AS t ON t.trip_id = s.trip_id
),
hop_pairs AS (
    SELECT DISTINCT station_id AS a, next_station_id AS b
    FROM day_stops
    WHERE next_station_id IS NOT NULL AND next_station_id <> station_id
),
reference AS (
    SELECT DISTINCT ON (hp.a, hp.b)
           hp.a, hp.b,
           x.trip_id AS ref_trip_id,
           LEAST(x.pos, y.pos) AS pos_from,
           GREATEST(x.pos, y.pos) AS pos_to
    FROM hop_pairs AS hp
    JOIN all_stops AS x ON x.station_id = hp.a
    JOIN all_stops AS y ON y.trip_id = x.trip_id AND y.station_id = hp.b
    ORDER BY hp.a, hp.b, abs(y.pos - x.pos) DESC, x.trip_id
),
local_hops AS (
    SELECT r.a AS hop_a, r.b AS hop_b, s.station_id AS a, s.next_station_id AS b
    FROM reference AS r
    JOIN all_stops AS s
      ON s.trip_id = r.ref_trip_id
     AND s.pos >= r.pos_from
     AND s.pos < r.pos_to
    WHERE s.next_station_id <> s.station_id
)
SELECT sa.name AS od, sb.name AS do_stacji,
       count(*) AS odcinki_lokalne,
       round(ST_Distance(sa.geom::geography, sb.geom::geography) / 1000) AS km_prosto,
       round(sum(ST_Distance(la.geom::geography, lb.geom::geography)) / 1000) AS km_po_trasie,
       round((sum(ST_Distance(la.geom::geography, lb.geom::geography))
              / ST_Distance(sa.geom::geography, sb.geom::geography))::NUMERIC, 2) AS stosunek
FROM local_hops AS l
JOIN stations AS sa ON sa.station_id = l.hop_a
JOIN stations AS sb ON sb.station_id = l.hop_b
JOIN stations AS la ON la.station_id = l.a
JOIN stations AS lb ON lb.station_id = l.b
GROUP BY l.hop_a, l.hop_b, sa.name, sb.name, sa.geom, sb.geom
HAVING count(*) > 1
ORDER BY stosunek DESC;
```

## Ograniczenia

- **Proste linie.** Bez `shapes.txt` geometria odcinka to odcinek prosty między stacjami (`ST_MakeLine`), a nie przebieg torów.
- **`trips_per_day` to kursy przejeżdżające odcinek**, także te, które na jego końcach się nie zatrzymują. Nie jest to to samo co `departures_per_day` stacji, które liczy tylko postoje.
- **Kurs wzorcowy to heurystyka.** Zależy od tego, czy w danych jest kurs zatrzymujący się na wszystkich stacjach pośrednich. Jeśli takiego kursu nie ma, przejazd zostaje jednym dłuższym odcinkiem. Objazdy wyłapuje kontrola wyżej.
- **Kursy przejeżdżające przez tę samą stację dwa razy** (pętle) mogą dać nietypowy wybór kursu wzorcowego. W obecnych danych nie zaobserwowano problemów.
