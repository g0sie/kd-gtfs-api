# Jakość danych GTFS – `stops.txt` i `stop_times.txt`

Kontrola wykonana 22–24.10.2026 w QGIS (warstwy z plików tekstowych + zapytania SQL w warstwie wirtualnej) na pełnych, niefiltrowanych plikach z `data/gtfs/`.

## Podsumowanie

Dane są spójne. Nie znaleziono duplikatów, przystanków bez kursów ani brakujących odwołań między plikami. Przy imporcie trzeba zwrócić uwagę na trzy rzeczy: **typy kolumn**, **hierarchię stacja–peron** oraz **stacje zagraniczne**.

| Sprawdzenie | Wynik |
|---|---|
| Liczba rekordów w `stops.txt` | 1019 (387 stacji, 632 perony) |
| Hierarchia stacja–peron | kompletna |
| Stacje poza Polską | 56 stacji (24 w Niemczech, 32 w Czechach) + 55 peronów (111 rekordów) |
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

### 4. Stacje zagraniczne

Koleje Dolnośląskie obsługują połączenia transgraniczne, więc część stacji leży w Niemczech i Czechach. Stacje zagraniczne wyznaczono w QGIS: obrys Polski (rozpuszczone granice województw), a następnie wyodrębnienie obiektów z `stops.txt` rozłącznych z tym obrysem. Stacje położone tuż przy granicy (m.in. Görlitz / Zgorzelec) sprawdzono ręcznie na podkładzie OpenStreetMap – żadna polska stacja nie trafiła na listę.

Poza Polską jest **111 rekordów: 56 stacji i 55 peronów**.

| Kraj | Stacje |
|---|---|
| Niemcy (DE) | 24 |
| Czechy (CZ) | 32 |

**Decyzja zespołu: importujemy wszystkie stacje 1:1, bez filtrowania.** Powody:
- `stop_times` odwołuje się do tych stacji, więc ich usunięcie wymagałoby skracania kursów i psułoby spójność kluczy obcych,
- linie transgraniczne nie urywają się na mapie, a odjazdy pokazują prawdziwy cel podróży,
- jeśli jakaś analiza będzie potrzebowała tylko stacji w Polsce, dodamy flagę `is_domestic` wyznaczoną przestrzennie z granicą Polski, zamiast kasować dane.

**Przy imporcie:** nic nie filtrować. Każda stacja dostaje flagę `is_domestic` (opisaną w kontrakcie API, #37). Lista poniżej jest podstawą tej flagi i jest sprawdzana testem importu. Perony dziedziczą wartość po stacji nadrzędnej.

#### Niemcy (24 stacje)

| `stop_id` | Nazwa |
|---|---|
| 1413064 | Arnsdorf (b Dresden) |
| 1413069 | Bautzen |
| 1413079 | Bischofswerda |
| 1413090 | Breitendorf |
| 1413113 | Demitz-Thumitz |
| 1413124 | Dresden Hbf |
| 1413125 | Dresden Industriegelände |
| 1413126 | Dresden Mitte |
| 1413127 | Dresden-Klotzsche |
| 1413128 | Dresden-Neustadt |
| 1413131 | Forst (Lausitz) |
| 1413133 | Gersdorf (b Görlitz) |
| 1413151 | Großharthau |
| 1413142 | Görlitz |
| 1413143 | Görlitz-Rauschwalde |
| 1413202 | Kubschütz |
| 1413206 | Langebrück (Sachs) |
| 1413220 | Löbau (Sachs) |
| 1413279 | Pommritz |
| 1413287 | Radeberg |
| 1413292 | Reichenbach (Oberlausitz) |
| 1413304 | Seitschen |
| 1413369 | Weickersdorf (Sachs) |
| 1413421 | Zoblitz |

#### Czechy (32 stacje)

| `stop_id` | Nazwa |
|---|---|
| 1413072 | Bernartice u Trutnova |
| 1413114 | Desná |
| 1413115 | Desná-Pustinská |
| 1413116 | Desná-Riedlova vila |
| 1413121 | Dolní Polubný |
| 1413153 | Harrachov |
| 1413157 | Jablonec nad Nisou |
| 1413158 | Jablonec nad Nisou centrum |
| 1413159 | Jablonec nad Nisou dolní n. |
| 1413160 | Jablonec nad Nisou zastávka |
| 1413161 | Jablonecké Paseky |
| 1413190 | Kořenov |
| 1413191 | Kořenov zastávka |
| 1413194 | Kralovec |
| 1413195 | Křenov |
| 1413216 | Liberec |
| 1413217 | Liberec-Rochlice |
| 1413215 | Libeč |
| 1413218 | Lichkov |
| 1413226 | Lučany nad Nisou |
| 1413254 | Nová Ves nad Nisou |
| 1413281 | Proseč nad Nisou |
| 1413312 | Smržovka |
| 1413313 | Smržovka dolní nádraží |
| 1413314 | Smržovka střed |
| 1413315 | Smržovka-Luční |
| 1413349 | Tanvald |
| 1413350 | Tanvald zastávka |
| 1413352 | Trutnov hl. n. |
| 1413353 | Trutnov střed |
| 1413361 | Vesec u Liberce |
| 1413362 | Vratislavice nad Nisou |

### 5. Typy kolumn

Automatyczne wykrywanie typów w QGIS dawało mylące wyniki:
- `location_type` zostało rozpoznane jako wartość logiczna (prawda/fałsz), bo w pliku występują tylko `0` i `1`,
- `stop_id` było rozpoznawane różnie w różnych plikach, a porównania liczby z tekstem w SQLite potrafią po cichu nic nie znaleźć.

Wszystkie `stop_id` w obecnym feedzie są liczbami całkowitymi (konwersja na liczbę nie dała żadnych wartości NULL).

**Przy imporcie:** wymuszać typy zamiast polegać na autodetekcji:
- `stop_id`, `parent_station` – ten sam typ w `stops.txt` i `stop_times.txt` (specyfikacja GTFS traktuje identyfikatory jako tekst, więc bezpieczniej trzymać je jako tekst, nawet jeśli dziś są liczbami),
- `location_type` – liczba całkowita.

W bazie wszystkie identyfikatory są typu `TEXT`, a tabele surowe `raw_*` trzymają wszystko jako tekst.

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
