# Decyzje projektowe

Ustalenia z pull requestów, które nie wynikają wprost z kodu ani z innych dokumentów. Każda decyzja ma link do PR-a, w którym zapadła. Szczegóły są w podlinkowanych dokumentach, a tutaj tylko sama decyzja.

Nową decyzję dopisujemy w tym samym PR-ze, w którym zapadła.

## Dane i liczenie kursów

- **Dni wzorcowe:** roboczy wtorek **2026-11-24** (747 kursów) i weekendowa niedziela **2026-11-22** (617 kursów). Liczby „na dobę” podajemy zawsze dla konkretnej daty, nigdy dla dnia tygodnia. Uzasadnienie: [reference-day.md](reference-day.md). ([#35](https://github.com/g0sie/kd-gtfs-api/pull/35))
- **Kalendarz w bazie:** jest rozwinięty na konkretne dni w tabeli `service_dates` (typ `DATE`, z uwzględnionymi wyjątkami z `calendar_dates.txt`). ([#35](https://github.com/g0sie/kd-gtfs-api/pull/35), [#38](https://github.com/g0sie/kd-gtfs-api/pull/38))
- **Stacje zagraniczne:** importujemy **wszystkie** stacje, bez filtrowania. Stacje krajowe od zagranicznych odróżnia flaga `is_domestic`, wyznaczona na podstawie listy 56 stacji zagranicznych (24 DE, 32 CZ) z [data-quality.md](data-quality.md) i sprawdzana testem importu. ([#36](https://github.com/g0sie/kd-gtfs-api/pull/36), [#37](https://github.com/g0sie/kd-gtfs-api/pull/37))
- **Czasy w bazie:** sekundy od północy doby kursu w kolumnach `arrival_sec` i `departure_sec` (np. `24:48:00` = 89280). Typ `TIME` nie obsługuje czasów powyżej 24:00. ([#37](https://github.com/g0sie/kd-gtfs-api/pull/37))
- **Nazwa linii:** pole `line` = `COALESCE(route_short_name, route_long_name)`. Import zapisuje puste `route_short_name` jako `NULL`, więc `NULLIF` nie jest potrzebne. 7 linii ma tylko `route_long_name`. ([#37](https://github.com/g0sie/kd-gtfs-api/pull/37), [#38](https://github.com/g0sie/kd-gtfs-api/pull/38))
- **Tabele surowe `raw_*`:** tworzy je skrypt importu `db/import_gtfs.py`, a nie `init.sql`. Kolumny są tekstem, dokładnie jak w plikach GTFS (np. daty `YYYYMMDD`). Tabele istnieją dopiero po uruchomieniu importu i są tworzone od nowa przy każdym uruchomieniu, więc nie warto w nich niczego ręcznie zmieniać. Służą do sprawdzania danych i zapytań z [reference-day.md](reference-day.md); tabele docelowe tworzy z nich `db/transform.sql`. ([#18](https://github.com/g0sie/kd-gtfs-api/issues/18))

## Odjazdy

- **Bez ostatniego przystanku kursu:** odjazdy liczymy bez ostatniego postoju, zarówno w `departures_per_day`, jak i w `departures_by_hour`. W bazie są to wiersze z `pickup_type <> 1`. Zapytania muszą mieć **dokładnie ten warunek**, bo na nim opiera się częściowy indeks `stop_times_departures_idx`. ([#37](https://github.com/g0sie/kd-gtfs-api/pull/37), [#38](https://github.com/g0sie/kd-gtfs-api/pull/38))
- **`departures_by_hour` ma 25 pozycji (0–24):** `hour: 24` to odjazdy po północy doby kursowej (czas ≥ `24:00:00`). Dzięki temu na wykresie nie ma sztucznego „garbu” o północy. ([#37](https://github.com/g0sie/kd-gtfs-api/pull/37))

## API

- **Parametr `date`** jest w `/stations/{id}/departures`, `/stats` i `/segments`. ([#37](https://github.com/g0sie/kd-gtfs-api/pull/37))
- **Domyślna data:**
  - `/stats` i `/segments`: zawsze 2026-11-24,
  - `/departures`: dzisiejsza data, a gdy leży poza zakresem feedu (19.10–12.12.2026), 2026-11-24. Dzięki temu API nie zwraca pustych list po wygaśnięciu rozkładu.

  ([#37](https://github.com/g0sie/kd-gtfs-api/pull/37))

- **Odległości** liczymy jako `geography` (metry na elipsoidzie). Kolumny `geom` są typu `geometry(Point, 4326)`, więc w zapytaniach trzeba rzutować: `ST_Distance(geom::geography, punkt::geography)` i `ORDER BY geom::geography <-> punkt::geography`. ([#38](https://github.com/g0sie/kd-gtfs-api/pull/38))
- **Odcinki** (`/segments`) będą funkcją SQL z parametrem daty, a nie zwykłym widokiem, żeby dało się je liczyć dla dowolnego dnia. ([#37](https://github.com/g0sie/kd-gtfs-api/pull/37))

## Wartości referencyjne do testów

Policzone na migawce z `data/gtfs/` ([#37](https://github.com/g0sie/kd-gtfs-api/pull/37)). Liczby kursów potwierdzono też na zaimportowanej bazie.

|                                     | 2026-11-24 (wt)     | 2026-11-22 (nd)     |
| ----------------------------------- | ------------------- | ------------------- |
| kursy                               | 747                 | 617                 |
| wiersze `stop_times`                | 10 298              | 8 679               |
| odjazdy (bez ostatniego przystanku) | 9 551               | 8 062               |
| `hour: 24`                          | 48                  | 48                  |
| `hour: 0`                           | 0                   | 12                  |
| najwięcej odjazdów                  | Wrocław Główny, 253 | Wrocław Główny, 190 |

W całym feedzie: 1838 postojów z `pickup_type = 1` i 24 753 pozostałych ([#38](https://github.com/g0sie/kd-gtfs-api/pull/38)).

## Do zrobienia przy podpinaniu bazy (#21)

- **Testy `distance_m`:** mock API liczy odległość wzorem haversine (kula), a baza przez `geography` (elipsoida). Przy przejściu na bazę trzeba poprawić wartości w testach. ([#39](https://github.com/g0sie/kd-gtfs-api/pull/39))
- **`seconds_to_time`:** potrzebna funkcja zamieniająca sekundy z bazy na `HH:MM:SS`, bez `% 24` (89280 → `"24:48:00"`). ([#39](https://github.com/g0sie/kd-gtfs-api/pull/39))
- **Host bazy w kontenerze:** w kontenerze API `DATABASE_URL` ma host `db` (nazwa usługi w `docker-compose.yml`), a nie `127.0.0.1`. ([#39](https://github.com/g0sie/kd-gtfs-api/pull/39))
- **Zakres feedu:** `FEED_START` i `FEED_END` brać z kalendarza w bazie (najwcześniejszy `start_date`, najpóźniejszy `end_date`), a nie wpisywać na sztywno. ([#39](https://github.com/g0sie/kd-gtfs-api/pull/39))

## Do zrobienia przy hostingu

- **CORS** ze zmiennej środowiskowej zamiast wpisanego na sztywno `localhost:5173`. ([#39](https://github.com/g0sie/kd-gtfs-api/pull/39))

## Organizacja zadań

- **#20** zawężone do testów endpointów, bo same endpointy na danych przykładowych powstały w [#39](https://github.com/g0sie/kd-gtfs-api/pull/39).
