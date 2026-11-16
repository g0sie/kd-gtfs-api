# CLAUDE.md

Mapa projektu dla Claude Code i nowych osób w zespole. Zamiast przepisywać szczegóły, odsyła do właściwych dokumentów.

## Projekt

Baza danych, API i mapa internetowa stacji Kolei Dolnośląskich, zbudowane na rozkładzie jazdy w formacie GTFS. Aplikacja odpowiada na dwa pytania: jaka stacja jest najbliżej wskazanego punktu i jakie są z niej najbliższe odjazdy oraz które odcinki i stacje mają najwięcej kursów. Projekt zespołowy (4 osoby) na Politechnice Wrocławskiej, semestr zimowy 2026/27.

**Stack:** PostgreSQL + PostGIS, Python + FastAPI, React (Vite) + Leaflet, QGIS, Docker Compose, `pytest`, GitHub Actions.

## Dokumentacja

| Plik | Co w nim jest |
|---|---|
| [README.md](README.md) | Cel projektu, uruchomienie bazy w Dockerze, najczęstsze problemy, zespół i harmonogram. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Jak pracujemy: issue → branch → PR z przeglądem, pary recenzentów, tablica zadań, styl kodu. |
| [docs/plan-projektu.md](docs/plan-projektu.md) | Pierwotny plan: zakres, architektura, podział zadań, harmonogram, ryzyka. Tabela API w pkt 6 jest historyczna. |
| [docs/api-contract.md](docs/api-contract.md) | Obowiązujący kontrakt API: endpointy, parametry (m.in. `date`), format odpowiedzi i błędów. |
| [docs/decisions.md](docs/decisions.md) | Decyzje z pull requestów, których nie widać w kodzie, z linkami do PR-ów, oraz wartości referencyjne do testów. |
| [docs/data-quality.md](docs/data-quality.md) | Kontrola jakości `stops.txt` i `stop_times.txt`: hierarchia stacja–peron, lista 56 stacji zagranicznych, typy kolumn. |
| [docs/reference-day.md](docs/reference-day.md) | Dzień wzorcowy i reguła, czy kurs jedzie danego dnia (`calendar` + `calendar_dates`). |
| [data/README.md](data/README.md) | Źródło danych GTFS, ważność rozkładu, data pobrania, licencja i atrybucja. |
| [db/init.sql](db/init.sql) | Schemat bazy z komentarzami: tabele, klucze, indeksy przestrzenne i indeks odjazdów. |
| [src/frontend/README.md](src/frontend/README.md) | Praca nad frontendem lokalnie, poza kontenerem. |
| [docs/segments.md](docs/segments.md) | Budowa odcinków sieci dla `/segments`: definicja, odcinki nieskierowane, rozbijanie kursów przyspieszonych, szkic funkcji SQL i wartości kontrolne. |
**Decyzje projektowe są w [docs/decisions.md](docs/decisions.md).** Zanim zmienisz sposób liczenia kursów, odjazdów, dat lub odległości, sprawdź ten plik. Nową decyzję dopisz tam w tym samym PR-ze, w którym zapadła.

## Struktura repozytorium

```
db/             schemat bazy (init.sql) i skrypty importu
src/api/        API (FastAPI), kod w src/api/app/
src/frontend/   aplikacja webowa (React + Leaflet)
data/gtfs/      migawka GTFS, nie edytujemy jej ręcznie
qgis/           projekty QGIS
tests/          testy pytest
docs/           dokumentacja
```

## Najważniejsze komendy

Komendy uruchamiamy z głównego katalogu repozytorium, o ile nie zaznaczono inaczej.

```bash
# Baza (PostgreSQL + PostGIS); wcześniej: cp .env.example .env
docker compose up -d
docker compose down          # zatrzymanie, dane zostają
docker compose down -v       # zatrzymanie i usunięcie danych (init.sql wykona się ponownie)

# API (http://localhost:8000/docs)
pip install -r requirements.txt
uvicorn app.main:app --app-dir src/api --reload

# Frontend (http://localhost:5173)
cd src/frontend
npm install
npm run dev

# Testy
python -m pytest
```

## Konwencje

- Jedno zadanie = jedno issue = jeden branch = jeden PR. Nie pushujemy bezpośrednio na `main`.
- Branch: `<numer-issue>-krotki-opis`, np. `18-import-gtfs`.
- Commity po angielsku, w trybie rozkazującym i opisowo: `Add GTFS import script`, a nie `update`.
- PR scalamy przez **Create a merge commit**, bez squasha. Każdy PR ma przegląd innej osoby.
- Nazwy plików w `docs/` po angielsku. Treść dokumentacji po polsku.
- Python: PEP 8, `snake_case` dla funkcji i zmiennych, `CamelCase` dla klas, bez zakomentowanego kodu i testowych `print`.
- Nie commitujemy `.env`, plików IDE, `node_modules/` ani dużych danych (miejsce na nie: `data/raw/`).

Szczegóły: [CONTRIBUTING.md](CONTRIBUTING.md).
