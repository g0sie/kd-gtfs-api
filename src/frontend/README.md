# Frontend

Aplikacja webowa z mapą stacji Kolei Dolnośląskich: React (Vite) i Leaflet (`react-leaflet`).

Docelowo frontend startuje razem z resztą projektu przez `docker compose up` (patrz [główny README](../../README.md)). Ta instrukcja dotyczy pracy nad frontem lokalnie, poza kontenerem.

## Wymagania

- Node.js w wersji 20.19+ lub 22.12+ (wymóg Vite),
- npm (instaluje się razem z Node.js).

## Uruchomienie

Wszystkie komendy uruchamiamy w katalogu `src/frontend/`:

```bash
cd src/frontend
npm install
npm run dev
```

Aplikacja będzie pod adresem http://localhost:5173. Zmiany w kodzie widać w przeglądarce od razu, bez ponownego uruchamiania.

`npm install` wystarczy uruchomić raz po sklonowaniu repozytorium i ponownie po każdej zmianie w `package.json`.

## Inne komendy

| Komenda           | Co robi                                                  |
| ----------------- | -------------------------------------------------------- |
| `npm run build`   | buduje wersję produkcyjną do katalogu `dist/`            |
| `npm run preview` | uruchamia lokalnie zbudowaną wersję z `dist/`            |
| `npm run lint`    | sprawdza kod ESLintem                                    |

## Dane z API

Front pobiera stacje z endpointu `GET /stations` (kontrakt: [docs/api-contract.md](../../docs/api-contract.md)). Wszystkie endpointy korzystają z bazy, więc front pokazuje prawdziwe dane z rozkładu GTFS.

Adres API jest w zmiennej `VITE_API_URL`. Domyślnie to `http://localhost:8000`, więc przy pracy lokalnej nie trzeba nic ustawiać. Inny adres wpisz w pliku `.env` w katalogu `src/frontend/`:

```bash
cp .env.example .env
```

Po zmianie `.env` trzeba ponownie uruchomić `npm run dev`, bo Vite czyta ten plik tylko przy starcie.

## Uruchomienie razem z API

Potrzebne są dwa terminale.

1. API, w głównym katalogu repozytorium:

   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --app-dir src/api --reload
   ```

   API działa pod http://localhost:8000, dokumentacja pod http://localhost:8000/docs.

2. Front, w katalogu `src/frontend/`:

   ```bash
   npm run dev
   ```

Gdy API nie działa, zamiast mapy pojawi się komunikat z adresem, pod którym front go szuka.

Front można też uruchomić w Dockerze, bez Node.js, razem z bazą i API: `docker compose up --build` w głównym katalogu repozytorium (opis w [głównym README](../../README.md)).

## Mapa

Kliknięcie w mapę pokazuje najbliższą stację i odległość do niej (`GET /stations/nearest`).

Kliknięcie stacji albo przycisk „Pokaż odjazdy” w popupie najbliższej stacji otwiera panel z najbliższymi odjazdami, z wyborem daty i godziny (`GET /stations/{id}/departures`).

Przycisk „Statystyki” nad mapą otwiera panel z liczbą kursów i stacji, wykresem odjazdów w ciągu doby i rankingiem stacji z największą liczbą odjazdów dla wybranego dnia (`GET /stats`).

Przycisk „Odcinki” włącza warstwę odcinków między stacjami: kolor i grubość linii zależą od liczby kursów na dobę, a legenda w lewym dolnym rogu pokazuje klasy i pozwala wybrać dzień roboczy albo weekend (`GET /segments`).

Kafelki mapy pochodzą z OpenStreetMap. Atrybucja „© OpenStreetMap contributors” musi być zawsze widoczna na mapie.

## Uwagi

- Katalogi `node_modules/` i `dist/` są ignorowane przez Git, nie dodajemy ich do repozytorium.
- Plik `package-lock.json` commitujemy, żeby wszyscy mieli te same wersje paczek.
