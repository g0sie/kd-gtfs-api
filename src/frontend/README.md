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

Front pobiera stacje z endpointu `GET /stations` (kontrakt: [docs/api-contract.md](../../docs/api-contract.md)). Na razie API zwraca dane przykładowe. Gdy endpointy zaczną korzystać z zapytań do bazy, front pokaże prawdziwe stacje bez żadnych zmian.

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

## Mapa

Kafelki mapy pochodzą z OpenStreetMap. Atrybucja „© OpenStreetMap contributors” musi być zawsze widoczna na mapie.

## Uwagi

- Katalogi `node_modules/` i `dist/` są ignorowane przez Git, nie dodajemy ich do repozytorium.
- Plik `package-lock.json` commitujemy, żeby wszyscy mieli te same wersje paczek.
