# Dane

## Rozkład jazdy Kolei Dolnośląskich (GTFS)

- **Źródło:** https://kolejedolnoslaskie.pl/rozklady-gtfs/
- **Wydawca w pliku `feed_info.txt`:** kiedyPrzyjedzie.pl
- **Ważność rozkładu:** 08.10.2026 – 12.12.2026
- **Data pobrania:** 20.10.2026
- **Licencja:** strona źródłowa nie podaje nazwanej licencji. Wg informacji ze strony (sprawdzone 20.10.2026):
  statyczne rozkłady GTFS są bezpłatne na czas nieokreślony, ich użycie nie wymaga zgłoszenia ani zgody,
  korzystanie jest na własną odpowiedzialność, a dostęp ma charakter testowy.
- **Atrybucja:** Koleje Dolnośląskie S.A., dane GTFS, https://kolejedolnoslaskie.pl/rozklady-gtfs/

## Gdzie co leży

- `gtfs/` – wypakowana migawka GTFS (pliki `.txt`: `agency`, `calendar`, `calendar_dates`, `feed_info`, `routes`, `stop_times`, `stops`, `trips`). Pliki są w repozytorium, żeby projekt dało się uruchomić po sklonowaniu. Nie edytujemy ich ręcznie.
- `raw/` – miejsce na duże lub tymczasowe pliki pobrane z internetu. Katalog jest ignorowany przez Git.

## Uwagi o danych

- Brak pliku `shapes.txt`, więc geometrię odcinków budujemy ze stacji w kolejności kursu.
- Część czasów jest powyżej 24:00:00 (kursy po północy).
- Każdy kurs ma własny `service_id`, więc „kursy na dobę" liczymy dla ustalonego dnia wzorcowego.
- W `stops.txt` są stacje (`location_type=1`) i perony (`location_type=0`, z `parent_station`). `stop_times.txt` odwołuje się do peronów.
- Kilka stacji leży w Niemczech (np. Dresden) i przy imporcie je odfiltrowujemy.

## Aktualizacja danych

Po zmianie migawki zaktualizować datę pobrania i ważność rozkładu w tym pliku i opisać zmianę w commicie.
