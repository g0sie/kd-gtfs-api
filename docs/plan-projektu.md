# Mapa i API stacji Kolei Dolnośląskich

Projekt geoinformatyczny, Politechnika Wrocławska. Zespół 4-osobowy: Dominika, Michał, Weronika, Małgorzata.

> Dokument roboczy. Terminy w harmonogramie są orientacyjne i trzeba je dopasować do dat zajęć i oddania projektu.

## 1. Cel projektu

Zbudować bazę danych, API i mapę internetową na podstawie rozkładu jazdy Kolei Dolnośląskich (GTFS). Aplikacja ma odpowiadać na dwa pytania:

1. **Najbliższy pociąg:** gdzie jest najbliższa stacja od wskazanego punktu i jakie są z niej najbliższe odjazdy.
2. **Częstotliwość połączeń:** które odcinki i stacje sieci mają najwięcej kursów, a które najmniej.

Do tego jeden wykres i podstawowe statystyki oraz możliwość pobrania danych w formacie JSON/GeoJSON przez API.

## 2. Dane

- **Źródło:** pliki GTFS ze strony Kolei Dolnośląskich (https://kolejedolnoslaskie.pl/rozklady-gtfs/).
- **Ważność rozkładu:** 08.10.2026 – 12.12.2026 (`feed_info.txt`). Do projektu używamy jednego, stałego zestawu danych.
- **Zawartość (stan z przeglądu plików):**
  - 387 stacji i 634 perony (`stops.txt`; stacje mają `location_type=1`, perony `0` z `parent_station`),
  - 54 linie (D1–D96),
  - 1904 kursy,
  - ok. 27 tys. wpisów w `stop_times.txt`.
- **Pułapki w danych:**
  - brak `shapes.txt`, więc geometrię odcinków budujemy sami (linie między kolejnymi stacjami w kursie),
  - 190 czasów jest powyżej 24:00:00 (kursy po północy), co psuje zwykłe parsowanie czasu,
  - każdy kurs ma własny `service_id`, więc liczenie „kursów na dobę" wymaga wybrania dnia wzorcowego,
  - kilka stacji leży w Niemczech (Dresden itd.) i trzeba je odfiltrować,
  - `stop_times` odwołuje się do peronów, a na mapie pokazujemy stacje.
- **Do sprawdzenia:** licencja danych i wymagania co do podania źródła.

## 3. Zakres

**Rdzeń (obowiązkowo):**

- import GTFS do PostgreSQL/PostGIS,
- API: lista stacji (GeoJSON), najbliższe stacje do punktu, odjazdy ze stacji, odcinki z liczbą kursów, statystyki,
- mapa w przeglądarce (React + Leaflet): stacje, klik w mapę = „najbliższy pociąg", warstwa częstotliwości,
- jeden wykres i statystyki (np. odjazdy na dobę, ranking stacji),
- analiza i mapy w QGIS.

**Opcjonalnie (jeśli starczy czasu):**

- „Dokąd dojadę z…": stacje osiągalne bez przesiadki w 30/60/90 minut,
- „Białe plamy kolejowe": bufory od stacji i pokrycie gmin (wymaga granic administracyjnych, dodatkowy zbiór danych),
- wdrożenie w chmurze (Render, Neon/Supabase, Netlify).

**Poza zakresem:** planowanie tras z przesiadkami.

## 4. Technologie

| Warstwa                        | Technologia                                                    |
| ------------------------------ | -------------------------------------------------------------- |
| Baza danych                    | PostgreSQL + PostGIS                                           |
| API                            | Python, FastAPI                                                |
| Frontend                       | React (Vite), Leaflet (`react-leaflet`), wykres (np. Recharts) |
| Analiza i mapy                 | QGIS                                                           |
| Środowisko                     | Docker, `docker-compose`                                       |
| Repozytorium i praca zespołowa | GitHub (Projects/kanban, Pull Requesty), GitHub Actions        |
| Testy                          | `pytest`                                                       |

## 5. Architektura

```
pliki GTFS ──► skrypt importu (Python) ──► PostgreSQL + PostGIS ──► FastAPI ──► React + Leaflet
                                                   │
                                                   └──► QGIS (analiza, mapy)
```

Lokalnie wszystko uruchamiane przez `docker compose up`: usługi `db` (PostGIS), `api` (FastAPI) i `frontend`. Adres bazy przekazywany przez zmienną środowiskową `DATABASE_URL`, żeby późniejsze wdrożenie w chmurze wymagało tylko zmiany tej zmiennej.

## 6. Wstępny kontrakt API

Do uzgodnienia i doprecyzowania przez Weronikę i Małgorzatę w `docs/api-contract.md`.

| Endpoint                                     | Opis                                                                     | Odpowiedź             |
| -------------------------------------------- | ------------------------------------------------------------------------ | --------------------- |
| `GET /health`                                | sprawdzenie, że API działa                                               | JSON                  |
| `GET /stations`                              | wszystkie stacje                                                         | GeoJSON               |
| `GET /stations/nearest?lat=&lon=&limit=`     | najbliższe stacje do punktu                                              | GeoJSON z odległością |
| `GET /stations/{id}/departures?time=&limit=` | najbliższe odjazdy ze stacji                                             | JSON                  |
| `GET /segments`                              | odcinki między stacjami z liczbą kursów                                  | GeoJSON               |
| `GET /stats`                                 | statystyki (liczba stacji, kursów, ranking stacji, odjazdy w ciągu doby) | JSON                  |

## 7. Podział zadań

| Osoba          | Rola              | Odpowiada za                                                                                                                          |
| -------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Dominika**   | Baza i dane       | PostGIS, schemat tabel, import GTFS, zapytania SQL, cały `docker-compose.yml`                                                         |
| **Michał**     | QGIS i analiza    | kontrola jakości danych, definicja dnia wzorcowego, odcinki, analizy i mapy w QGIS, dokumentacja danych i analiz                      |
| **Weronika**   | API               | FastAPI i wszystkie endpointy (w tym `/stats`), testy `pytest`, `Dockerfile` API, kontrakt API                                        |
| **Małgorzata** | Frontend i GitHub | React + Leaflet + wykres, `Dockerfile` frontu, repozytorium, kanban i harmonogram, `CONTRIBUTING.md`, workflow CI/CD, szkielet README |

Treść README i dokumentacji piszą właściwe osoby (każdy opisuje swoją część), a Małgorzata pilnuje struktury.

**Propozycja wzajemnych przeglądów pull requestów:** Dominika ↔ Michał, Weronika ↔ Małgorzata. Każdy PR musi mieć przegląd innej osoby przed scaleniem.

## 8. Pierwsze zadania (do kanbanu)

**Małgorzata**

- [ ] Założyć repozytorium, dodać wszystkich jako współpracowników, `.gitignore`, struktura katalogów, szkielet README _(zrobić jako pierwsze)_
- [ ] Kanban (Todo / In Progress / Done) z zadaniami i osobami, wykres Gantta
- [ ] `CONTRIBUTING.md`: gałąź na zadanie, pull request z przeglądem, opisowe commity
- [ ] Zapytać prowadzącą o zgodę na PostgreSQL/PostGIS
- [ ] Szkielet Reacta (Vite + `react-leaflet`), mapa z kafelkami OSM (z atrybucją) i markerami z danych przykładowych
- [ ] Workflow GitHub Actions z `pytest` przy `push` i `pull_request`

**Weronika**

- [ ] Kontrakt API (`docs/api-contract.md`) razem z Małgorzatą _(na samym początku)_
- [ ] Szkielet FastAPI z `requirements.txt`, `Dockerfile` (z `CMD`), `/health`, endpointy zwracające dane przykładowe zgodnie z kontraktem
- [ ] Pierwszy test `pytest`

**Dominika**

- [ ] `docker-compose.yml` z `postgis/postgis`, wolumen, port, `.env.example`
- [ ] Schemat tabel w `db/init.sql` z indeksem przestrzennym (GiST)
- [ ] Skrypt importu GTFS (czasy po 24:00, bez stacji niemieckich) z testem liczby rekordów

**Michał**

- [ ] Wczytać dane w QGIS z plików CSV, sprawdzić jakość (stacje a perony, współrzędne, duplikaty), wnioski do `docs/`
- [ ] Ustalić dzień wzorcowy do liczenia kursów na dobę
- [ ] Opisać logikę budowy odcinków (pary kolejnych stacji + liczba kursów) w `docs/segments.md`

## 9. Wstępny harmonogram

| Tydzień | Daty        | Plan                                                                                                         |
| ------- | ----------- | ------------------------------------------------------------------------------------------------------------ |
| 1       | 19–25.10    | Repozytorium, kanban, kontrakt API, baza w Dockerze i schemat, szkielety API i frontu, jakość danych         |
| 2       | 26.10–1.11  | Import GTFS, API na danych przykładowych, mapa na danych przykładowych, dzień wzorcowy, CI z `pytest`        |
| 3       | 2–8.11      | API na prawdziwej bazie: `/stations`, `/stations/nearest`; front podpięty do API; odcinki jako widok w bazie |
| 4       | 9–15.11     | `/stations/{id}/departures`, `/segments`; warstwa częstotliwości na mapie; mapy w QGIS                       |
| 5       | 16–22.11    | `/stats` i wykres; testy z bazą w CI                                                                         |
| 6       | 23–29.11    | Poprawki, dopracowanie UI, dokumentacja; opcjonalnie rozszerzenia                                            |
| 7       | 30.11–6.12  | Dokumentacja końcowa, README, porządki w kodzie, przegląd checklisty                                         |
| 8       | 7–13.12     | Próba prezentacji; opcjonalnie wdrożenie w chmurze                                                           |
| 9+      | wg terminów | Bufor i prezentacja końcowa                                                                                  |

Gantta można zrobić w Excelu na podstawie tej tabeli i dodać do `docs/`.

## 10. Zasady pracy w Gicie

- Jedna gałąź na zadanie, scalanie przez pull request z przeglądem innej osoby.
- Opisowe komunikaty commitów, np. `Add spatial query for nearest stations`, a nie `update`.
- Commity regularnie przez cały semestr, a nie jednym wrzutem na końcu. Historia ma pokazywać wkład każdej z czterech osób.
- Zadania w kanbanie zawsze z przypisaną osobą i aktualnym statusem.
- W repozytorium nie trzymamy plików IDE (`.vscode/`, `.idea/`), `node_modules/` ani dużych surowych danych.
- Kod: `snake_case` dla funkcji i zmiennych, `CamelCase` dla klas (PEP 8), krótkie funkcje, podział na moduły, bez zakomentowanego kodu i testowych `print`.

## 11. Wymagania prowadzącej a nasz plan

| Wymaganie z checklisty                                  | Jak je spełniamy                                          | Kto                            |
| ------------------------------------------------------- | --------------------------------------------------------- | ------------------------------ |
| Nazwa repo, współpracownicy, README                     | punkt 8, zadania Małgorzaty                               | Małgorzata                     |
| Struktura katalogów, brak zbędnych plików               | `db/`, `src/`, `data/`, `tests/`, `docs/`, `.gitignore`   | Małgorzata                     |
| Kanban z przypisaniami, harmonogram, Gantt              | GitHub Projects + Excel                                   | Małgorzata                     |
| Regularne commity, opisowe komunikaty, wkład wszystkich | zasady z punktu 10, PR z przeglądem                       | wszyscy                        |
| Czysty kod (PEP 8, moduły, bez `print`)                 | punkt 10                                                  | wszyscy                        |
| `requirements.txt`, `Dockerfile`, `docker-compose.yml`  | API i front mają `Dockerfile`, compose z bazą i wolumenem | Weronika, Małgorzata, Dominika |
| Workflow CI/CD z testami i zielony pipeline             | GitHub Actions z `pytest`                                 | Małgorzata, Weronika           |
| Baza danych z danymi                                    | PostgreSQL + PostGIS, import GTFS                         | Dominika                       |
| Wykres + statystyka                                     | `/stats` + wykres w Reactcie                              | Weronika, Małgorzata           |
| Pobranie danych (JSON/GeoJSON/API)                      | endpointy FastAPI                                         | Weronika                       |

## 12. Ryzyka i otwarte pytania

- **Zgoda na PostgreSQL/PostGIS:** w checklistcie podano SQLite/SpatiaLite/MongoDB „np.", ale warto potwierdzić z prowadzącą. _(Małgorzata)_
- **Licencja danych KD:** sprawdzić warunki użycia i sposób podania źródła.
- **Dzień wzorcowy:** każdy kurs ma własny `service_id`, więc definicję „kursów na dobę" trzeba ustalić wcześnie. _(Michał)_
- **Wąskie gardło:** baza z importem blokuje prawdziwe endpointy. Dominika powinna jak najszybciej dać choćby minimalny import (stacje i `stop_times`), a reszta pracuje na danych przykładowych.
- **Obciążenie Małgorzaty:** front + GitHub to dużo, dlatego `/stats` i testy są po stronie Weroniki, a `docker-compose` po stronie Dominiki.
- **CI a baza:** testy wymagające bazy potrzebują PostGIS jako usługi w GitHub Actions.
- **PostGIS w chmurze:** przed wdrożeniem sprawdzić, że wybrany darmowy hosting bazy pozwala na `CREATE EXTENSION postgis;`.
- **Terminy:** uzupełnić daty oddania i prezentacji, i dopasować harmonogram.

## 13. Hosting (na końcu, opcjonalnie)

Najpierw wszystko działa lokalnie w Dockerze (`docker compose up`). Dopiero potem sprawdzamy wdrożenie, np.: baza w Neon lub Supabase, API na Renderze, front na Renderze lub Netlify. Pamiętać o CORS, o tym, że darmowe API na Renderze usypia po 15 minutach bez ruchu (przed prezentacją „obudzić"), i że darmowa baza Supabase może się wstrzymać po tygodniu bez aktywności. Warunki darmowych planów trzeba sprawdzić u dostawców przed decyzją.
