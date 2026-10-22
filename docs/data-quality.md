# Jakość danych GTFS – `stops.txt` i `stop_times.txt`

Kontrola wykonana 22.10.2026 w QGIS (warstwy z plików tekstowych + zapytania SQL w warstwie wirtualnej) na pełnych, niefiltrowanych plikach z `data/gtfs/`.

## Podsumowanie

Dane są spójne. Nie znaleziono duplikatów, przystanków bez kursów ani brakujących odwołań między plikami. Przy imporcie trzeba zwrócić uwagę na trzy rzeczy: **typy kolumn**, **hierarchię stacja–peron** oraz **stacje spoza Dolnego Śląska**.

| Sprawdzenie | Wynik |
|---|---|
| Liczba rekordów w `stops.txt` | 1019 (387 stacji, 632 perony) |
| Hierarchia stacja–peron | kompletna |
| Stacje poza Dolnym Śląskiem | 83 stacje + 102 perony (185 rekordów) |
| Duplikaty nazw stacji | brak |
| Duplikaty współrzędnych stacji | brak |
| Perony / stacje bez kursów | brak |
| `stop_id` z `stop_times.txt` nieistniejące w `stops.txt` | brak |
| Kursy wskazujące bezpośrednio na stację | brak |
| Perony z własną lokalizacją | 0 z 632 |

## Szczegóły i obsługa przy imporcie

### 1. Hierarchia stacja–peron

- `location_type = 1` – stacja (387 rekordów), `parent_station` puste.
- `location_type = 0` – peron (632 rekordy), `parent_station` wskazuje na `stop_id` stacji.
- Każdy peron ma istniejącą stację nadrzędną, żadna stacja nie ma rodzica.

**Przy imporcie:** rozdzielać stacje i perony po `location_type`. Kursy z `stop_times.txt` są przypisane wyłącznie do peronów, więc żeby powiązać kurs ze stacją, trzeba przejść przez `parent_station`.

### 2. Powtarzające się nazwy to nie duplikaty

W `stops.txt` ta sama nazwa występuje wielokrotnie (np. `Bardo Przyłęk` 3 razy: stacja `1413065` i dwa perony). Wynika to wyłącznie z hierarchii. Wśród samych stacji nie ma ani powtórzonych nazw, ani powtórzonych współrzędnych.

**Przy imporcie:** nie deduplikować rekordów po nazwie ani po współrzędnych. Usunięcie „duplikatów” usunęłoby perony, do których odwołują się kursy.

### 3. Perony nie mają własnej lokalizacji

Wszystkie 632 perony mają dokładnie te same współrzędne co ich stacja.

**Przy imporcie:** geometria peronów nie wnosi żadnej informacji. Do map i analiz przestrzennych wystarczą stacje (`location_type = 1`).

### 4. Stacje spoza Dolnego Śląska

Po przecięciu z granicą województwa poza regionem zostaje 83 stacji i 102 peronów (185 z 1019 rekordów), np. `Arnsdorf (b Dresden)`. Są to głównie stacje na trasach transgranicznych i w sąsiednich województwach.

**Do decyzji zespołu:**
- odrzucić je przy imporcie – wtedy kursy przejeżdżające przez te stacje zostaną obcięte do części w regionie, a `stop_times` będą miały odwołania do nieistniejących przystanków, które trzeba odfiltrować,
- albo zachować je i tylko oznaczyć (np. kolumna `w_regionie`), żeby trasy transgraniczne pozostały kompletne.

Filtrowanie trzeba zrobić **po** wczytaniu pełnego feedu, nie przed, bo inaczej sprawdzanie spójności `stop_times` daje fałszywe błędy.

### 5. Typy kolumn

Automatyczne wykrywanie typów w QGIS dawało mylące wyniki:
- `location_type` zostało rozpoznane jako wartość logiczna (prawda/fałsz), bo w pliku występują tylko `0` i `1`,
- `stop_id` było rozpoznawane różnie w różnych plikach, a porównania liczby z tekstem w SQLite potrafią po cichu nic nie znaleźć.

Wszystkie `stop_id` w obecnym feedzie są liczbami całkowitymi (konwersja na liczbę nie dała żadnych wartości NULL).

**Przy imporcie:** wymuszać typy zamiast polegać na autodetekcji:
- `stop_id`, `parent_station` – ten sam typ w `stops.txt` i `stop_times.txt` (specyfikacja GTFS traktuje identyfikatory jako tekst, więc bezpieczniej trzymać je jako tekst, nawet jeśli dziś są liczbami),
- `location_type` – liczba całkowita.

## Zapytania kontrolne

Zapytania dla warstwy wirtualnej QGIS (SQLite). Warstwy nazywają się `stops` i `stop_times`. Każde zapytanie uruchamiać osobno. W PostgreSQL `group_concat` należy zamienić na `string_agg`.

```sql
-- liczba stacji i peronów
SELECT location_type, COUNT(*) FROM stops GROUP BY location_type;

-- unikalność stop_id (oczekiwany wynik: pusto)
SELECT stop_id, COUNT(*) AS n FROM stops GROUP BY stop_id HAVING n > 1;

-- perony bez istniejącej stacji nadrzędnej (pusto)
SELECT p.stop_id, p.stop_name, p.parent_station
FROM stops p
LEFT JOIN stops s ON p.parent_station = s.stop_id
WHERE p.location_type = 0 AND s.stop_id IS NULL;

-- powtórzone nazwy stacji (pusto)
SELECT stop_name, COUNT(*) AS n, group_concat(stop_id, ', ') AS ids
FROM stops WHERE location_type = 1
GROUP BY stop_name HAVING n > 1;

-- powtórzone współrzędne stacji (pusto)
SELECT stop_lat, stop_lon, COUNT(*) AS n, group_concat(stop_name, '; ') AS nazwy
FROM stops WHERE location_type = 1
GROUP BY stop_lat, stop_lon HAVING n > 1;

-- perony ze współrzędnymi swojej stacji (wynik: 632)
SELECT COUNT(*)
FROM stops p
JOIN stops s ON p.parent_station = s.stop_id
WHERE p.location_type = 0
  AND p.stop_lat = s.stop_lat AND p.stop_lon = s.stop_lon;

-- perony i stacje bez kursów (pusto)
SELECT stop_id, stop_name, 'peron bez kursów' AS problem
FROM stops
WHERE location_type = 0
  AND stop_id NOT IN (SELECT DISTINCT stop_id FROM stop_times)
UNION ALL
SELECT s.stop_id, s.stop_name, 'stacja bez kursów' AS problem
FROM stops s
WHERE s.location_type = 1
  AND NOT EXISTS (
    SELECT 1 FROM stops p
    JOIN stop_times st ON st.stop_id = p.stop_id
    WHERE p.parent_station = s.stop_id
  );

-- stop_id z stop_times nieistniejące w stops (pusto)
SELECT DISTINCT st.stop_id
FROM stop_times st
LEFT JOIN stops s ON st.stop_id = s.stop_id
WHERE s.stop_id IS NULL;

-- kursy wskazujące bezpośrednio na stację (pusto)
SELECT DISTINCT st.stop_id
FROM stop_times st
JOIN stops s ON st.stop_id = s.stop_id
WHERE s.location_type = 1;
```
