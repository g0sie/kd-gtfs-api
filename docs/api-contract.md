## Ustalenia

| Temat | Ustalenie |
|---|---|
| Adres lokalny | `http://localhost:8000` |
| Dokumentacja interaktywna | `http://localhost:8000/docs` (generuje FastAPI) |
| Format danych | JSON; dane przestrzenne jako GeoJSON (`FeatureCollection`) |
| Kolejność współrzędnych w GeoJSON | **[lon, lat]** (zgodnie ze standardem GeoJSON) |
| Kolejność współrzędnych w parametrach zapytania | `lat=` i `lon=` podawane osobno, po nazwie |
| Odległość | w **metrach**, liczba zmiennoprzecinkowa zaokrąglona do 1 m |
| Czas odjazdu | tekst `HH:MM:SS`; godziny mogą przekraczać 23 (np. `25:10:00` to 01:10 następnego dnia, tak jak w GTFS) |
| Data | tekst `YYYY-MM-DD` (strefa Europa/Warszawa) |
| Identyfikatory stacji | tekst (`id` jako string), zgodny z `stop_id` stacji w GTFS (`location_type=1`), np. `"1413380"`; identyfikatory nie są krótkie ani numerowane od 1 |
| Zakres stacji | wszystkie stacje z GTFS importowane 1:1, bez filtrowania (także zagraniczne, np. czeskie; patrz #18); stację krajową od zagranicznej odróżnia pole `is_domestic` |
| Dzień wzorcowy | definicja w `docs/reference-day.md` (#9); wszystkie wartości "na dobę" (`trips_per_day`, `departures_per_day`, `trips_count`, `departures_by_hour`) liczone są dla dnia wzorcowego |
| CORS | API zezwala na zapytania z frontu (inny port) |
| Błędy | JSON `{"detail": "..."}`; kod 404 gdy brak zasobu, 422 gdy złe parametry |
| Dane na tym etapie | **przykładowe** (kilka stacji), prawdziwa baza od tygodnia 3; liczby i identyfikatory w przykładach poniżej są poglądowe |

## GET /health

Sprawdzenie, że API działa.

Odpowiedź 200:
```json
{"status": "ok"}
```

## GET /stations

Wszystkie stacje (bez peronów).

Odpowiedź 200 (`FeatureCollection`, każdy `Feature` to punkt):
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [17.0366, 51.0985]},
      "properties": {"id": "1413380", "name": "Wrocław Główny", "is_domestic": true}
    }
  ]
}
```

| Pole w `properties` | Opis |
|---|---|
| `id` | identyfikator stacji (`stop_id`, tekst) |
| `name` | nazwa stacji |
| `is_domestic` | `true` dla stacji w Polsce, `false` dla zagranicznych (np. czeskich: Trutnov, Harrachov, Smržovka); front może je rysować inaczej |

## GET /stations/nearest

Najbliższe stacje do wskazanego punktu, od najbliższej. Uwzględnia także stacje zagraniczne (rozróżnienie przez `is_domestic`).

| Parametr | Typ | Wymagany | Domyślnie | Zakres |
|---|---|---|---|---|
| `lat` | liczba | tak | - | od -90 do 90 |
| `lon` | liczba | tak | - | od -180 do 180 |
| `limit` | liczba całkowita | nie | 5 | od 1 do 50 |

Przykład: `/stations/nearest?lat=51.11&lon=17.03&limit=3`

Odpowiedź 200: `FeatureCollection` jak w `/stations`, posortowany rosnąco po odległości,
a w `properties` dodatkowo `distance_m` (odległość w metrach):
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

Najbliższe odjazdy ze stacji (ze wszystkich jej peronów) w wybranym dniu, od podanej godziny.

W `calendar.txt` każdy kurs ma własny `service_id` z wąskim zakresem obowiązywania, więc same godziny nie wystarczają: endpoint uwzględnia tylko kursy, które jadą w dniu `date`.

| Parametr | Typ | Wymagany | Domyślnie | Opis |
|---|---|---|---|---|
| `id` (w ścieżce) | tekst | tak | - | identyfikator stacji |
| `date` | tekst `YYYY-MM-DD` | nie | dzisiejsza data (Europa/Warszawa) | dzień, dla którego zwracane są odjazdy (kursy z aktywnym `service_id` w tym dniu) |
| `time` | tekst `HH:MM:SS` | nie | aktualna godzina (Europa/Warszawa) | odjazdy od tej godziny w dniu `date` |
| `limit` | liczba całkowita | nie | 10 | od 1 do 100 |

Zasady:
- Czas odjazdu liczony jest względem doby kursu w GTFS: odjazd `24:48:00` kursu z dnia `date` jest zwracany w dniu `date` (po odjazdach z godzin 0-23), a nie w następnym dniu.
- Jeśli w dniu `date` nie jeździ żaden kurs, odpowiedź to 200 z pustą listą `departures`.

Przykład: `/stations/1413380/departures?date=2026-10-24&time=08:00:00&limit=5`

Odpowiedź 200:
```json
{
  "station": {"id": "1413380", "name": "Wrocław Główny"},
  "date": "2026-10-24",
  "departures": [
    {
      "departure_time": "08:12:00",
      "line": "D1",
      "headsign": "Jelenia Góra",
      "trip_id": "D1_0001"
    }
  ]
}
```

| Pole | Opis |
|---|---|
| `date` | dzień, dla którego policzono odjazdy (wartość użyta lub domyślna) |
| `departure_time` | `HH:MM:SS`, może przekraczać 23 |
| `line` | `route_short_name`; gdy go brak (w danych 7 linii ma tylko `route_long_name`, np. `D91/D64`), API zwraca `route_long_name` w zastępstwie. Pole **nigdy nie jest `null` ani puste**, front nie musi się zabezpieczać |
| `headsign` | kierunek kursu |
| `trip_id` | identyfikator kursu |

Błędy: 404 gdy nie ma takiej stacji, 422 gdy `time` lub `date` ma zły format.

## GET /segments

Odcinki między kolejnymi stacjami wraz z liczbą kursów na dobę wzorcową
(definicja dnia wzorcowego: `docs/reference-day.md`; logika budowania odcinków: `docs/segments.md`).

Odpowiedź 200 (`FeatureCollection`, każdy `Feature` to linia):
```json
{
  "type": "FeatureCollection",
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

## GET /stats

Podstawowe statystyki do wykresu i panelu na froncie. Wszystkie wartości dotyczą doby wzorcowej.

Odpowiedź 200 (liczby poglądowe):
```json
{
  "stations_count": 387,
  "trips_count": 1838,
  "top_stations": [
    {"id": "1413380", "name": "Wrocław Główny", "departures_per_day": 210}
  ],
  "departures_by_hour": [
    {"hour": 5, "departures": 12}
  ]
}
```

| Pole | Opis |
|---|---|
| `stations_count` | liczba stacji (bez peronów) |
| `trips_count` | liczba kursów na dobę wzorcową (nie w całym feedzie) |
| `top_stations` | ranking **10** stacji wg liczby odjazdów na dobę wzorcową, malejąco |
| `departures_by_hour` | liczba odjazdów w każdej godzinie doby (0-23), zawsze 24 pozycje; dane do wykresu. Odjazdy z czasem ≥ `24:00:00` trafiają do godziny `hour = czas_godzina - 24`, np. `24:48:00` liczy się do `hour: 0` (nie ma `hour: 24`). Suma `departures` ze wszystkich godzin równa się łącznej liczbie odjazdów doby wzorcowej |

## Otwarte kwestie

- [ ] Małgorzata: zatwierdzenie kontraktu (komentarz w PR).
- [ ] Dominika: potwierdzenie, w jakiej formie czasy po 24:00 są w bazie (od tego zależy liczenie `hour` w `departures_by_hour`).
- [ ] Michał: potwierdzenie, że `trips_per_day`, `departures_per_day` i `trips_count` liczone są zgodnie z `docs/reference-day.md`.
- [ ] Ustalić, jak wyznaczamy `is_domestic` (np. na podstawie granicy Polski), bo GTFS nie ma takiej kolumny.
