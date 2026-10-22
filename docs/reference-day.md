# Dzień wzorcowy — jak liczymy „kursy na dobę”

## TL;DR

| Typ dnia | Data wzorcowa | Kursów (aktywnych `service_id`) |
|---|---|---|
| **Roboczy** | **wtorek 2026-11-24** | **747** |
| **Weekendowy** | **niedziela 2026-11-22** | **617** |
| (pomocniczo) sobota | 2026-11-21 | 618 |

W `/stats` i na mapie zawsze podajemy liczbę kursów **dla konkretnej daty**, liczoną regułą poniżej. Domyślnie: dni z tabeli.

## Dane wejściowe

- `calendar.txt` — 1838 wierszy, 1838 unikalnych `service_id` (1 wiersz = 1 kurs).
- `calendar_dates.txt` — 1056 wyjątków, wszystkie `service_id` istnieją w `calendar.txt`.
- Zakres danych: **2026-10-19 – 2026-12-12**.

## Reguła: czy kurs jedzie danego dnia `D`

```
kurs jedzie w D  ⇔
   ( start_date ≤ D ≤ end_date  AND  calendar.<dzień_tygodnia(D)> = 1
     AND NOT EXISTS calendar_dates(service_id, D, exception_type = 2) )
   OR EXISTS calendar_dates(service_id, D, exception_type = 1)
```

Czyli: bierzemy kalendarz bazowy, potem `exception_type = 1` **dodaje** kurs w tym dniu, `exception_type = 2` go **usuwa**. Wyjątek zawsze wygrywa z kalendarzem.

Liczba kursów na dobę = `COUNT(DISTINCT service_id)` spełniających regułę dla jednej daty.

### Czego NIE robić

- **Nie liczyć wierszy `calendar.txt`** (1838). Większość kursów występuje w dwóch wersjach: jedna ważna 19–24.10, druga 25.10–12.12 (np. `1000_453340` / `1002_453342`). Suma wierszy liczy ten sam kurs podwójnie.
- **Nie liczyć „po dniu tygodnia” bez daty** (np. „wszystkie z `tuesday = 1`”) — łapie obie wersje okresowe i ignoruje wyjątki.
- **Nie pomijać `calendar_dates`** — np. 11.11 kalendarz bazowy daje 747, a w rzeczywistości jedzie 620.

## Szkic zapytania (SQL)

```sql
-- :d = data w formacie 'YYYYMMDD', :dow = nazwa kolumny dnia (np. tuesday)
WITH base AS (
  SELECT service_id FROM calendar
  WHERE :d BETWEEN start_date AND end_date
    AND tuesday = 1                         -- kolumna zależna od :d
),
added   AS (SELECT service_id FROM calendar_dates WHERE date = :d AND exception_type = 1),
removed AS (SELECT service_id FROM calendar_dates WHERE date = :d AND exception_type = 2)
SELECT COUNT(*) AS kursy FROM (
  SELECT service_id FROM base
  EXCEPT SELECT service_id FROM removed
  UNION  SELECT service_id FROM added
);
```

## Wyniki dla całego okresu

| Okres / dzień | Roboczy (pn / wt–pt) | Sobota | Niedziela | Uwagi |
|---|---|---|---|---|
| 19–23.10 | 757 / 756 | — | — | okres przejściowy, 16 kursów wyłączonych wyjątkami codziennie |
| 24–25.10 | — | 642 | 629 | 25.10: +12 kursów „śr+nd” ważnych tylko 25–28.10 |
| 26.10 – 12.12 (stabilnie) | **748 / 747** | **618** | **617** | |

Poniedziałek ma +1 kurs (`1579_453965`, tylko poniedziałki, do 07.12).

### Dni nietypowe (do wykluczenia jako wzorcowe)

| Data | Kursy | Co się dzieje |
|---|---|---|
| 19–23.10 | 756–757 | inny zestaw kursów niż w reszcie okresu + 16 wyłączeń |
| 25.10 (nd) | 629 | dodatkowe kursy okresowe 25–28.10 |
| 28.10 (śr) | 763 | +8 / −4 (podmiana kursów, prawdopodobnie zmiana organizacji ruchu) |
| 01.11 (nd) | 617 | Wszystkich Świętych: +171 weekendowych / −299 roboczych — na niedzielę nic to nie zmienia, ale wyjątki są |
| **11.11 (śr)** | **620** | Święto Niepodległości — rozkład świąteczny (≈ sobotni) zamiast roboczego |
| 12.11 (czw) | 748 | +1 kurs (`1579_453965`, normalnie poniedziałkowy) |
| 16–18.11 | 748 / 751 / 745 | drobne podmiany (+4/−4, +8/−4, −2) |

## Dlaczego te dni

- **Wtorek 24.11** — środek stabilnego okresu, zero wyjątków w `calendar_dates`, nie sąsiaduje ze świętem (10.11 odpada jako dzień przed 11.11, 17.11 ma wyjątki). Wynik 747 = typowa wartość dla wt–pt w całym okresie 26.10–12.12.
- **Niedziela 22.11** — zero wyjątków, ta sama wartość (617) co każda „czysta” niedziela od 08.11. 01.11 odpada jako święto, 25.10 jako dzień z kursami okresowymi.
- Oba dni są w tym samym tygodniu, więc porównanie robocze/weekend jest uczciwe.

## Czy wynik jest sensowny

- **Spójny wewnętrznie:** każdy „czysty” wtorek od 27.10 daje 747, każda czysta niedziela od 08.11 daje 617. Brak skoków bez wyjaśnienia w `calendar_dates`.
- **Święto zachowuje się poprawnie:** 11.11 spada z 747 do 620, czyli do poziomu weekendowego — tak jak powinno.
- **1 `service_id` = 1 kurs — potwierdzone na `trips.txt`:** 1838 kursów, 1838 unikalnych `trip_id`, 1838 unikalnych `service_id`, maks. 1 kurs na `service_id`. Każdy `service_id` z `calendar.txt` ma kurs i odwrotnie. Liczenie `COUNT(trip_id)` z joinem po aktywnych `service_id` daje dokładnie te same wartości (747 / 617 / 618).
- **Proporcja weekend/roboczy (~83%) jest w porządku.** To sieć kolejowa regionalna (Dolny Śląsk, 54 linie, kierunki typu Wrocław Główny, Legnica, Jelenia Góra, Szklarska Poręba Górna), nie komunikacja miejska. W weekend wyraźnie spadają linie dojazdowe (np. `364843`: 44 → 18, `364805`: 28 → 12, `364822`: 43 → 22), a linie dalekie i turystyczne trzymają poziom albo rosną (`364823`: 14 → 20, `364806`: 9 → 13). Aktywnych linii: 53 we wtorek, 51 w niedzielę.

### Docelowe zapytanie (z `trips`)

```sql
WITH active AS (
  SELECT service_id FROM calendar
  WHERE :d BETWEEN start_date AND end_date AND tuesday = 1   -- kolumna zależna od :d
  EXCEPT SELECT service_id FROM calendar_dates WHERE date = :d AND exception_type = 2
  UNION  SELECT service_id FROM calendar_dates WHERE date = :d AND exception_type = 1
)
SELECT t.route_id, COUNT(*) AS kursy          -- bez GROUP BY: suma dla całej sieci
FROM trips t JOIN active a USING (service_id)
GROUP BY t.route_id;
```

Uwagi do `trips.txt`: `direction_id` jest puste w całym pliku (kierunek tylko z `trip_headsign`), a `block_id` łączy dwie wersje okresowe tego samego kursu (np. `1_452001` i `2_452002` mają ten sam blok), więc nie nadaje się do liczenia kursów.
