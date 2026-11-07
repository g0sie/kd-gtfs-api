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

## Dane

Na razie mapa korzysta z danych przykładowych w kształcie odpowiedzi API (GeoJSON) z pliku `src/data/sampleStations.json`. Po uruchomieniu API zostaną one zastąpione prawdziwymi zapytaniami.

## Mapa

Kafelki mapy pochodzą z OpenStreetMap. Atrybucja „© OpenStreetMap contributors” musi być zawsze widoczna na mapie.

## Uwagi

- Katalogi `node_modules/` i `dist/` są ignorowane przez Git, nie dodajemy ich do repozytorium.
- Plik `package-lock.json` commitujemy, żeby wszyscy mieli te same wersje paczek.
