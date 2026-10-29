## Ustalenia

| Temat | Ustalenie |
|---|---|
| Adres lokalny | `http://localhost:8000` |
| Dokumentacja interaktywna | `http://localhost:8000/docs` (generuje FastAPI) |
| Format danych | JSON; dane przestrzenne jako GeoJSON (`FeatureCollection`) |
| Kolejność współrzędnych w GeoJSON | **[lon, lat]** (zgodnie ze standardem GeoJSON) |
| Kolejność współrzędnych w parametrach zapytania | `lat=` i `lon=` podawane osobno, po nazwie |
| Odległość | w **metrach**, liczba zmiennoprzecinkowa zaokrąglona do 1 m; liczona jako odległość geodezyjna na elipsoidzie (typ geography w PostGIS), więc działa też dla stacji za granicą |
| Czas odjazdu | tekst `HH:MM:SS`; godziny mogą przekraczać 23 (np. `25:10:00` to 01:10 następnego dnia, tak jak w GTFS) |
| Data | tekst `YYYY-MM-DD` (strefa Europa/Warszawa) |
| Identyfikatory stacji | tekst (`id` jako string), zgodny z `stop_id` stacji w GTFS (`location_type=1`), np. `"1413380"`; identyfikatory nie są krótkie ani numerowane od 1 |
| Zakres stacji | wszystkie stacje z GTFS importowane 1:1, bez filtrowania (także zagraniczne, np. czeskie; patrz #18); stację krajową od zagranicznej odróżnia pole `is_domestic` |
| Dzień wzorcowy | definicja w `docs/reference-day.md` (#9). Dwa dni: roboczy wtorek 2026-11-24 (747 kursów) i weekendowy niedziela 2026-11-22 (617 kursów). Wartości „na dobę" podawane są zawsze dla konkretnej daty (parametr `date`), a nie dla dnia tygodnia. |
| Domyślna data | `/departures`: dzisiejsza data, a gdy leży poza zakresem obowiązywania feedu (feed jest ważny do 2026-12-12), dzień wzorcowy roboczy 2026-11-24. `/stats` i `/segments`: zawsze 2026-11-24|
| CORS | API zezwala na zapytania z frontu (inny port) |
| Błędy | JSON `{"detail": "..."}`; kod 404 gdy brak zasobu, 422 gdy złe parametry |
| Dane na tym etapie | **przykładowe** (kilka stacji), prawdziwa baza od tygodnia 3; liczby i identyfikatory w przykładach poniżej są poglądowe, z wyjątkiem `stations_count` i `trips_count` |

## GET /health

Sprawdzenie, że API działa.

Odpowiedź 200:
```json
{"status": "ok"}
```

## GET /stations

Wszystkie stacje (bez peronów), także zagraniczne.

Odpowiedź 200 (`FeatureCollection`, każdy `Feature` to punkt):
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [17.0366, 51.0985]},
      "properties": {"id": "1413380", "name": "Wrocław Główny", "is_domestic": true}
    },
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [15.0, 51.15]},
      "properties": {"id": "1413390", "name": "Görlitz", "is_domestic": false}
    },
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [13.73, 51.04]},
      "properties": {"id": "1413395", "name": "Dresden Hbf", "is_domestic": false}
    },
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [15.91, 50.56]},
      "properties": {"id": "1413400", "name": "Trutnov", "is_domestic": false}
    }
  ]
}
```

| Pole w `properties` | Opis |
|---|---|
| `id` | identyfikator stacji (`stop_id`, tekst) |
| `name` | nazwa stacji |
| `is_domestic` | `true` dla stacji w Polsce, `false` dla zagranicznych (24 niemieckie, np. Dresden, Görlitz; 32 czeskie, np. Trutnov, Harrachov, Smržovka); front może je rysować inaczej. Wyznaczane przestrzennie względem granicy Polski przy imporcie (PostGIS); metoda i lista stacji zagranicznych w `docs/data-quality.md` (#8) |

## GET /stations/nearest

Najbliższe stacje do wskazanego punktu, od najbliższej. Uwzględnia także stacje zagraniczne (rozróżnienie przez `is_domestic`).

| Parametr | Typ | Wymagany | Domyślnie | Zakres |
|---|---|---|---|---|
| `lat` | liczba | tak | - | od -90 do 90 |
| `lon` | liczba | tak | - | od -180 do 180 |
| `limit` | liczba całkowita | nie | 5 | od 1 do 50 |

Przykład: `/stations/nearest?lat=51.11&lon=17.03&limit=3`

Odpowiedź 200: `FeatureCollection` jak w `/stations`, posortowany rosnąco po odległości,
a w `properties` dodatkowo `distance_m` (odległość w metrach, liczona jako `geography`):
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [17.0366, 51.0985]},
      "properties": {"id": "1413380", "name": "Wrocław Główny", "is_domestic": true, "distance_m": 1480.0}
    }
  ]
}
```

Błąd 422: brak `lat`/`lon`, wartość spoza zakresu lub nie liczba.

## GET /stations/{id}/departures

Najbliższe odjazdy ze stacji (ze wszystkich jej peronów, czyli po `parent_station`) w wybranym dniu, od podanej godziny.

W `calendar.txt` każdy kurs ma własny `service_id` z wąskim zakresem obowiązywania, więc same godziny nie wystarczają: endpoint uwzględnia tylko kursy, które jadą w dniu `date`.

| Parametr | Typ | Wymagany | Domyślnie | Opis |
|---|---|---|---|---|
| `id` (w ścieżce) | tekst | tak | - | identyfikator stacji |
| `date` | tekst `YYYY-MM-DD` | nie | dzisiejsza data (Europa/Warszawa); gdy poza zakresem feedu (ważny do 2026-12-12) - 2026-11-24 | dzień, dla którego zwracane są odjazdy (kursy z aktywnym `service_id` w tym dniu) |
| `time` | tekst `HH:MM:SS` | nie | aktualna godzina (Europa/Warszawa) | odjazdy od tej godziny w dniu `date` |
| `limit` | liczba całkowita | nie | 10 | od 1 do 100 |

Zasady:
- Czas odjazdu liczony jest względem doby kursu w GTFS: odjazd `24:48:00` kursu z dnia `date` jest zwracany w dniu `date` (po odjazdach z godzin 0-23), a nie w następnym dniu.
- Ostatni przystanek kursu nie jest odjazdem (kurs tam kończy bieg), więc nie jest zwracany.
- Jeśli w dniu `date` nie jeździ żaden kurs, odpowiedź to 200 z pustą listą `departures`.
- Pole `date` w odpowiedzi zawsze zawiera datę faktycznie użytą (także gdy zadziałała data domyślna dnia wzorcowego).

Przykład: `/stations/1413380/departures?date=2026-10-24&time=08:00:00&limit=5`

Odpowiedź 200:
```json
{
  "station": {"id": "1413380", "name": "Wrocław Główny"},
  "date": "2026-11-24",
  "departures": [
    {
      "departure_time": "08:12:00",
      "line": "D1",
      "headsign": "Jelenia Góra",
      "trip_id": "51384888_452001"
    }
  ]
}
```

| Pole | Opis |
|---|---|
| `date` | dzień, dla którego policzono odjazdy (wartość użyta lub domyślna) |
| `departure_time` | `HH:MM:SS`, może przekraczać 23 |
| `line` | `route_short_name`; gdy go brak lub jest pusty (w danych 7 linii ma tylko `route_long_name`, np. `D91/D64`), API zwraca `route_long_name` w zastępstwie. Pole **nigdy nie jest `null` ani puste**, front nie musi się zabezpieczać |
| `headsign` | kierunek kursu |
| `trip_id` | identyfikator kursu, np. `51384888_452001` |

Błędy: 404 gdy nie ma takiej stacji, 422 gdy `time` lub `date` ma zły format.

## GET /segments

Odcinki między kolejnymi stacjami wraz z liczbą kursów w wybranym dniu (definicja dnia wzorcowego: `docs/reference-day.md`; logika budowania odcinków: `docs/segments.md`, #10).

| Parametr | Typ | Wymagany | Domyślnie | Opis |
|---|---|---|---|---|
| `date` | tekst `YYYY-MM-DD` | nie | `2026-11-24` | dzień, dla którego liczone są kursy na odcinkach (dla weekendu: `2026-11-22`) |

Przykład: `/segments?date=2026-11-22`

Odpowiedź 200 (`FeatureCollection` z dodatkowym polem `date`, każdy `Featur`e to linia):
```json
{
  "type": "FeatureCollection",
  "date": "2026-11-24",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "LineString", "coordinates": [[17.0366, 51.0985], [16.1546, 51.2175]]},
      "properties": {
        "from_station_id": "1413380",
        "from_station_name": "Wrocław Główny",
        "to_station_id": "1413385",
        "to_station_name": "Legnica",
        "trips_per_day": 38
      }
    }
  ]
}
```

| Pole w | Opis |
|---|---|
| `trips_per_day` | liczba kursów aktywnych w dniu `date`, które przejeżdżają odcinek (odcinki budowane według `docs/segments.md`) |

Błąd 422: `date` w złym formacie.

## GET /stats

Podstawowe statystyki do wykresu i panelu na froncie. Wszystkie wartości dotyczą dnia `date`.

| Parametr | Typ | Wymagany | Domyślnie | Opis |
|---|---|---|---|---|
| `date` | tekst `YYYY-MM-DD` | nie | `2026-11-24` | dzień, dla którego liczone są kursy na odcinkach (dla weekendu: `2026-11-22`) |

Przykład: `/stats?date=2026-11-24`

Odpowiedź 200 (`stations_count` i `trips_count` prawdziwe dla 2026-11-24, reszta poglądowa):
```json
{
  "date": "2026-11-24",
  "stations_count": 387,
  "trips_count": 747,
  "top_stations": [
    {"id": "1413380", "name": "Wrocław Główny", "departures_per_day": 210}
  ],
  "departures_by_hour": [
    {"hour": 5, "departures": 12},
    {"hour": 24, "departures": 178}
  ]
}
```

| Pole | Opis |
|---|---|
| `date` | dzień, dla którego policzono statystyki |
| `stations_count` | liczba stacji (bez peronów); nie zależy od daty |
| `trips_count` | 	liczba kursów aktywnych w dniu `date` (nie w całym feedzie; liczba wierszy `calendar.txt` nie jest tą liczbą) |
| `top_stations` | 	ranking **10 stacji** wg `departures_per_day`, malejąco |
| `departures_per_day` | 	odjazdy z `stop_times` kursów aktywnych w dniu `date`, zsumowane po peronach stacji (`parent_station`), bez ostatniego przystanku kursu |
| `departures_by_hour` | 	liczba odjazdów w poszczególnych godzinach doby kursowej; dane do wykresu. Zawsze **25 pozycji**, `hour` od 0 do 24, w kolejności rosnącej. `hour: 0-23` to odjazdy z godzin 00:00-23:59, a `hour: 24` **oznacza odjazdy po północy**, czyli z czasem ≥ `24:00:00` (np. `24:48:00`). Dzięki temu wykres czyta się chronologicznie wzdłuż doby kursowej, a odjazdy z nocy dnia kursowego (`hour: 0-1`) nie mieszają się z odjazdami po północy. Odjazdy liczone tak jak w `departures_per_day` (bez ostatniego przystanku kursu), więc suma wszystkich pozycji równa się sumie odjazdów doby |

## Otwarte kwestie

- [ ] Michał/Małgorzata: potwierdzenie, że `departures_by_hour` liczy odjazdy tak samo jak `departures_per_day` (bez ostatniego przystanku kursu), a nie wszystkie wiersze `stop_times`; przy tej regule liczby w kubełkach będą nieco niższe niż w surowym rozkładzie `stop_times.txt`.
