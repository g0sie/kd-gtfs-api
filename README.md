# Mapa i API stacji Kolei Dolnośląskich

Projekt geoinformatyczny, Politechnika Wrocławska, semestr zimowy.

[![Testy](https://github.com/g0sie/kd-gtfs-api/actions/workflows/tests.yml/badge.svg)](https://github.com/g0sie/kd-gtfs-api/actions/workflows/tests.yml)

## Cel projektu

Budujemy bazę danych, API i mapę internetową na podstawie rozkładu jazdy Kolei Dolnośląskich (GTFS).

**Problem użytkowy:** rozkład Kolei Dolnośląskich jest publikowany jako pliki GTFS, czyli tabele tekstowe z kursami, przystankami i godzinami. Z takich plików trudno szybko odczytać, skąd najbliżej złapać pociąg i kiedy odjeżdża, ani jak gęsta jest sieć połączeń w regionie. Aplikacja pokazuje to na mapie i odpowiada na dwa pytania:

1. **Najbliższy pociąg:** jaka stacja jest najbliżej wskazanego punktu i jakie są z niej najbliższe odjazdy w wybranym dniu i o wybranej godzinie.
2. **Częstotliwość połączeń:** które odcinki i stacje mają najwięcej kursów na dobę, a które najmniej, w dniu roboczym i w weekend.

Do tego dochodzą wykres, podstawowe statystyki i możliwość pobrania danych w formacie JSON/GeoJSON przez API.

## Funkcje aplikacji

Mapa pokazuje wszystkie stacje z rozkładu (387, także stacje w Niemczech i Czechach) na podkładzie OpenStreetMap.

### Najbliższa stacja i odjazdy

Kliknięcie w dowolne miejsce mapy pokazuje najbliższą stację i odległość do niej. Przycisk „Pokaż odjazdy” w popupie otwiera panel z najbliższymi odjazdami z tej stacji.

![Najbliższa stacja z popupem i panelem odjazdów](docs/img/app-nearest.png)

### Panel odjazdów

Kliknięcie stacji otwiera panel z najbliższymi odjazdami: godzina, linia i kierunek. Datę i godzinę można wybrać; puste pola oznaczają dzisiejszą datę i aktualną godzinę. Kursy, które wyjeżdżają po północy, ale należą do rozkładu wybranego dnia, mają dopisek „następnego dnia”.

![Panel odjazdów z kursem po północy](docs/img/app-departures.png)

### Częstotliwość odcinków

Przycisk „Odcinki” włącza warstwę odcinków między stacjami. Kolor i grubość linii zależą od liczby kursów na dobę. Legenda pokazuje klasy i pozwala przełączyć dzień roboczy (24.11) albo weekend (22.11). Kliknięcie odcinka pokazuje obie stacje i liczbę kursów. Najgrubsze linie to promienie wychodzące z Wrocławia.

![Warstwa częstotliwości odcinków z legendą](docs/img/app-frequency.png)

### Statystyki

Przycisk „Statystyki” otwiera panel z liczbą kursów i stacji w wybranym dniu, wykresem odjazdów w ciągu doby i rankingiem 10 stacji z największą liczbą odjazdów. Ostatni słupek wykresu („po północy”) to odjazdy po północy kursów z danego dnia.

![Panel statystyk z wykresem i rankingiem stacji](docs/img/app-stats.png)

Pełny plan, podział zadań i harmonogram: [docs/plan-projektu.md](docs/plan-projektu.md).

## Dane

- Źródło: pliki GTFS ze strony [Kolei Dolnośląskich](https://kolejedolnoslaskie.pl/rozklady-gtfs/).
- Rozkład obowiązuje od 19.10.2026 do 12.12.2026.
- Migawka danych (wypakowane pliki GTFS, ok. 1,6 MB) jest w katalogu `data/gtfs/`, a opis źródła i daty pobrania w [data/README.md](data/README.md).
- Licencja i sposób podania źródła: opisane w [data/README.md](data/README.md).

## Technologie

| Warstwa        | Technologia            |
| -------------- | ---------------------- |
| Baza danych    | PostgreSQL + PostGIS   |
| API            | Python, FastAPI        |
| Frontend       | React, Leaflet         |
| Analiza i mapy | QGIS                   |
| Środowisko     | Docker, Docker Compose |
| CI/CD          | GitHub Actions         |

## Architektura

Skrypt importu wczytuje pliki GTFS do bazy PostgreSQL + PostGIS. API w FastAPI odpowiada na zapytania zapytaniami SQL do bazy i zwraca JSON/GeoJSON. Aplikacja webowa (React + Leaflet) pobiera dane z API i rysuje je na mapie. QGIS łączy się z tą samą bazą do analiz i map. Baza, API i front działają w kontenerach Docker Compose, a testy uruchamia GitHub Actions z własną bazą PostGIS.

```
data/gtfs/ → import (db/import_gtfs.py) → PostGIS → API (FastAPI) → aplikacja webowa (React + Leaflet)
                                              └──→ QGIS (analizy i mapy)
```

### Baza danych

<!-- Dominika: baza danych i import -->
Schemat tworzy [db/init.sql](db/init.sql) przy pierwszym starcie bazy: stacje (`stations`) z geometrią punktu, perony (`platforms`) przypisane do stacji, linie (`routes`), kursy (`trips`), dni kursowania (`service_dates`, kalendarz rozwinięty na konkretne daty) i postoje (`stop_times`, czasy w sekundach od północy doby kursu, także powyżej 24:00). Import ([db/import_gtfs.py](db/import_gtfs.py)) wczytuje pliki GTFS bez zmian do tabel `raw_*`, a [db/transform.sql](db/transform.sql) przerabia je na tabele docelowe i tworzy funkcje SQL `trips_on_date` (kursy jadące w danym dniu) i `segments_on_date` (odcinki z liczbą kursów, [docs/segments.md](docs/segments.md)). Decyzje dotyczące liczenia kursów i odjazdów: [docs/decisions.md](docs/decisions.md).

## Struktura repozytorium

```
db/             schemat bazy i skrypty SQL
src/api/        API (FastAPI)
src/frontend/   aplikacja webowa (React + Leaflet)
data/           migawka GTFS (data/gtfs/) i jej opis; duże pliki tymczasowe w data/raw/ (poza repozytorium)
qgis/           projekty QGIS
tests/          testy automatyczne
docs/           dokumentacja, plan projektu, kontrakt API
.github/        workflow CI/CD i szablony
```

## Wymagania

- Docker i Docker Compose,
- Python 3.12 (import danych i testy uruchamiane lokalnie),
- Node.js (tylko do pracy nad frontendem poza kontenerem),
- QGIS (tylko do analiz przestrzennych).

## Uruchomienie

### Najszybciej

Całą aplikację (baza PostgreSQL + PostGIS, API i aplikacja webowa) uruchamia Docker Compose, bez instalowania Node.js. Python 3.12 jest potrzebny tylko do jednorazowego importu danych.

1. Plik ze zmiennymi środowiskowymi (domyślne wartości działają bez zmian):

   ```bash
   cp .env.example .env
   ```

   W PowerShellu: `Copy-Item .env.example .env`.

2. Baza, API i front w tle:

   ```bash
   docker compose up --build -d
   ```

   Poczekaj, aż `docker compose ps` pokaże przy usłudze `db` status `(healthy)`.

3. Import danych, raz przy pierwszym uruchomieniu (bez niego mapa jest pusta). Aktywację środowiska opisuje sekcja [Środowisko Pythona](#środowisko-pythona):

   ```bash
   python -m venv .venv
   pip install -r requirements.txt
   python -m db.import_gtfs data/gtfs
   ```

4. Gotowe:
   - mapa: http://localhost:5173 (po imporcie odśwież stronę),
   - dokumentacja API: http://localhost:8000/docs.

Opcja `--build` przebudowuje obrazy API i frontu, więc widać w nich najnowszy kod. Szczegóły poszczególnych kroków i rozwiązania częstych problemów są niżej.

### Wymagania

- zainstalowany i uruchomiony Docker (Docker Desktop na Windowsie),
- Python 3.12.

### Środowisko Pythona

Import danych i testy uruchamiane są lokalnie, poza Dockerem. W katalogu repozytorium:

```bash
python -m venv .venv
```

Aktywacja: na Windowsie (PowerShell) `.\.venv\Scripts\Activate.ps1`, na Linuksie i macOS `source .venv/bin/activate`. Potem:

```bash
pip install -r requirements.txt
```

### Start bazy

1. Skopiuj plik ze zmiennymi środowiskowymi. Domyślne wartości działają bez zmian, a jeśli chcesz zmienić hasło, zrób to przed pierwszym startem bazy:
```bash
   cp .env.example .env
```

   W PowerShellu: `Copy-Item .env.example .env`. Plik `.env` jest w `.gitignore` i nie trafia do repozytorium.

2. Uruchom bazę w tle:

```bash
   docker compose up -d db
```

3. Sprawdź, że kontener działa:

```bash
   docker compose ps
```
   Poczekaj, aż usługa `db` będzie miała status `(healthy)`. Dopiero wtedy baza przyjmuje połączenia.

### Import danych

Przy włączonym środowisku Pythona i działającej bazie:

```bash
python -m db.import_gtfs data/gtfs
```

Skrypt wczytuje pliki GTFS z `data/gtfs/` do bazy. Czyści tabele i wczytuje dane od nowa, więc można go uruchamiać wielokrotnie, np. po `docker compose down -v`.

### Sprawdzenie PostGIS

Rozszerzenie PostGIS i tabele tworzy automatycznie [db/init.sql](db/init.sql) przy pierwszym starcie bazy. Żeby sprawdzić, że działa, podstaw wartości `POSTGRES_USER` i `POSTGRES_DB` z pliku `.env`:

```bash
docker compose exec db psql -U <POSTGRES_USER> -d <POSTGRES_DB> -c "SELECT postgis_version();"
```

Polecenie powinno zwrócić wersję PostGIS.

### Sprawdzenie danych

Po imporcie baza powinna zawierać 387 stacji:

```bash
docker compose exec db psql -U <POSTGRES_USER> -d <POSTGRES_DB> -c "SELECT count(*) FROM stations;"
```

Pełniejsze sprawdzenie to testy (sekcja [Testy](#testy)): przy działającej bazie z danymi testy bazy nie są pomijane.

### Zatrzymanie

```bash
docker compose down        # zatrzymuje kontenery, dane w wolumenie zostają
docker compose down -v     # zatrzymuje i usuwa dane (baza startuje od zera)
```

Dane bazy są przechowywane w wolumenie Dockera, więc przetrwają restart kontenera.

### Najczęstsze problemy

- **Port jest zajęty:** inny program (np. lokalny PostgreSQL) używa tego samego portu. Zmień port w pliku `.env`: `DB_PORT` (np. `5433`) i ten sam port w `DATABASE_URL`. Pliku `docker-compose.yml` nie trzeba ruszać. Jeśli to inny kontener Dockera, możesz go też zatrzymać: `docker ps`, potem `docker stop <nazwa>`.
- **Błąd połączenia zaraz po `up -d`** (np. `server closed the connection unexpectedly`, `connection refused` albo `the database system is shutting down`): przy pierwszym starcie baza wykonuje `db/init.sql` na serwerze tymczasowym i raz się restartuje, co trwa kilka sekund. Poczekaj, aż `docker compose ps` pokaże `(healthy)`, i powtórz polecenie. Healthcheck sprawdza połączenie przez TCP, więc `(healthy)` pojawia się dopiero po restarcie.
- **Brak tabel po aktualizacji repozytorium:** `db/init.sql` wykonuje się tylko na pustym wolumenie. Jeśli uruchamiałeś(-aś) bazę, zanim w repozytorium pojawił się schemat albo jego nowa wersja, użyj `docker compose down -v` i uruchom ponownie. Uwaga: to kasuje dane w bazie, więc potem trzeba ponowić import.
- **Zmiana hasła w `.env` nie działa:** baza inicjalizuje się tylko na pustym wolumenie. Użyj `docker compose down -v` i uruchom ponownie.
- **Połączenie z bazą wisi na Windowsie:** w `DATABASE_URL` używaj `127.0.0.1` zamiast `localhost`, który na Windowsie potrafi wisieć (IPv6). Tak jest już w `.env.example`.
- **Import łączy się z inną bazą niż w `.env`:** zmienna `DATABASE_URL` ustawiona w systemie ma pierwszeństwo przed plikiem `.env`. Sprawdź ją przez `$env:DATABASE_URL` (PowerShell) albo `echo $DATABASE_URL` (Linux / macOS).
- **PowerShell blokuje `Activate.ps1`:** `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- **Testy bazy padają po aktualizacji repozytorium:** import tworzy też funkcje SQL (np. `trips_on_date`), więc po zmianach w `db/transform.sql` trzeba go uruchomić ponownie: `python -m db.import_gtfs data/gtfs`.

Adresy po uruchomieniu:

- Aplikacja webowa (mapa): http://localhost:5173
- API i dokumentacja: http://localhost:8000/docs

## Pobieranie danych (API)

<!-- Weronika: API -->
API zwraca dane w formacie JSON, a stacje i odcinki jako GeoJSON, więc można je wczytać np. do QGIS albo własnego skryptu. Endpointy:

- `GET /health`: czy API działa i czy ma połączenie z bazą.
- `GET /stations`: wszystkie stacje z flagą `is_domestic` (stacja w Polsce albo za granicą).
- `GET /stations/nearest?lat=…&lon=…&limit=…`: stacje najbliższe wskazanemu punktowi, od najbliższej, z odległością w metrach (`distance_m`).
- `GET /stations/{id}/departures?date=…&time=…&limit=…`: najbliższe odjazdy ze stacji w wybranym dniu od wybranej godziny; odjazdy po północy mają godzinę od `24:00:00` w górę.
- `GET /segments?date=…`: odcinki między stacjami z liczbą kursów na dobę (`trips_per_day`).
- `GET /stats?date=…`: liczba kursów i stacji, ranking stacji z największą liczbą odjazdów i odjazdy w kolejnych godzinach doby.

Przykład:

```bash
curl "http://localhost:8000/stations/nearest?lat=51.11&lon=17.03&limit=3"
```

Pełny opis parametrów, wartości domyślnych i błędów: [docs/api-contract.md](docs/api-contract.md). Interaktywna dokumentacja, w której można wywołać każdy endpoint z przeglądarki: http://localhost:8000/docs.

## Analizy w QGIS

<!-- Michał: analizy w QGIS -->
Mapy częstotliwości połączeń zrobione w QGIS na danych z bazy (odcinki z funkcji `segments_on_date`, grubość linii według liczby kursów na dobę, na mapie tylko stacje obsługiwane danego dnia):

- dzień roboczy (24.11.2026): [docs/map-frequency-weekday.pdf](docs/map-frequency-weekday.pdf),
- niedziela (22.11.2026): [docs/map-frequency-sunday.pdf](docs/map-frequency-sunday.pdf).

Projekt QGIS z mapami: [qgis/frequency-maps.qgz](qgis/frequency-maps.qgz). Projekt łączy się z bazą z Dockera, więc przed otwarciem baza musi działać i mieć zaimportowane dane. Kontrola jakości danych w QGIS jest opisana w [docs/data-quality.md](docs/data-quality.md).

## Testy

Testy są w katalogu `tests/` i używają `pytest`. Testy endpointów `/stations`, `/stations/nearest` i odjazdów oraz testy importu potrzebują działającej bazy z zaimportowanym GTFS. Bez niej są pomijane (`SKIPPED`). Walidacja parametrów (422) i `/segments` są testowane bez bazy.

```bash
pip install -r requirements.txt
docker compose up -d db
python -m db.import_gtfs data/gtfs
python -m pytest
```

Testy uruchamiają się automatycznie w GitHub Actions przy każdym pushu i pull requeście. Workflow stawia własną bazę PostGIS, wykonuje `db/init.sql` i import, więc w CI przechodzą wszystkie testy, łącznie z testami bazy.

## Zespół

| Osoba      | Rola                                         |
| ---------- | -------------------------------------------- |
| Dominika   | Baza danych i import danych                  |
| Michał Adamowicz (@Whyfooo)     | QGIS i analiza przestrzenna                  |
| Małgorzata Derkacz (@g0sie) | Frontend i organizacja repozytorium (GitHub) |
| Weronika Mongiało (@wemon007)| API (FastAPI) i testy      |

## Harmonogram

Oddanie projektu: **26.11.2026**. Od **23.11.2026** obowiązuje feature freeze: nie dodajemy nowych funkcji, tylko poprawiamy błędy i dokumentację.

Harmonogram prowadzimy w widoku Roadmap w projekcie GitHub (pola Start date i Target date w zadaniach). Poniżej zrzuty ze stanu na 22.10.2026.

**Fazy projektu:**

![Harmonogram projektu: fazy](docs/harmonogram-gantt.png)

**Przykładowe zadania z tygodni 1–2:**

![Harmonogram projektu: zadania](docs/harmonogram-zadania.png)

Szczegółowy plan: [docs/plan-projektu.md](docs/plan-projektu.md).


## Zasady pracy

Jak zakładać branche, otwierać pull requesty i korzystać z tablicy zadań: [CONTRIBUTING.md](CONTRIBUTING.md).
