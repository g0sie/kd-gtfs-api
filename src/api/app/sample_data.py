"""Dane przykładowe do czasu podpięcia prawdziwej bazy (tydzień 3).

Stacje (id, nazwa, współrzędne, is_domestic) są prawdziwe, wzięte z bazy.
Odjazdy, odcinki i statystyki są poglądowe (poza trips_count dla 2026-11-24).
Nie zależą od daty: każda data zwraca te same wartości.
"""

STATIONS = [
    {
        "id": "1413380",
        "name": "Wrocław Główny",
        "lat": 51.097917,
        "lon": 17.037957,
        "is_domestic": True,
    },
    {
        "id": "1413210",
        "name": "Legnica",
        "lat": 51.214097,
        "lon": 16.16967,
        "is_domestic": True,
    },
    {
        "id": "1413171",
        "name": "Jelenia Góra",
        "lat": 50.90259,
        "lon": 15.75599,
        "is_domestic": True,
    },
    {
        "id": "1413142",
        "name": "Görlitz",
        "lat": 51.146841,
        "lon": 14.97833,
        "is_domestic": False,
    },
    {
        "id": "1413124",
        "name": "Dresden Hbf",
        "lat": 51.040374,
        "lon": 13.731484,
        "is_domestic": False,
    },
    {
        "id": "1413352",
        "name": "Trutnov hl. n.",
        "lat": 50.565261,
        "lon": 15.911056,
        "is_domestic": False,
    },
]

SEGMENTS = [
    {"from_id": "1413380", "to_id": "1413210", "trips_per_day": 38},
    {"from_id": "1413380", "to_id": "1413171", "trips_per_day": 24},
    {"from_id": "1413210", "to_id": "1413142", "trips_per_day": 12},
    {"from_id": "1413142", "to_id": "1413124", "trips_per_day": 10},
]


def _departure(time, short_name, long_name, headsign, trip_id):
    """route_short_name bywa puste (None), wtedy line bierze route_long_name."""
    return {
        "departure_time": time,
        "route_short_name": short_name,
        "route_long_name": long_name,
        "headsign": headsign,
        "trip_id": trip_id,
    }


DEPARTURES = {
    "1413380": [
        _departure("08:12:00", "D1", "Wrocław - Jelenia Góra", "Jelenia Góra", "51384888_452001"),
        _departure("08:40:00", "D2", "Wrocław - Legnica", "Legnica", "51384888_452002"),
        _departure("09:05:00", None, "D91/D64", "Görlitz", "51384888_452003"),
        _departure("24:48:00", "D1", "Wrocław - Jelenia Góra", "Jelenia Góra", "51384888_452004"),
    ],
    "1413210": [
        _departure("08:55:00", "D2", "Wrocław - Legnica", "Wrocław Główny", "51384888_452005"),
    ],
}


_HOURLY_VALUES = [
    4, 2, 0, 0, 6, 18, 42, 55, 50, 44, 38, 36, 40, 42, 46, 52, 60, 58, 48, 40, 34, 30, 24, 14, 12,
]

STATS = {
    "trips_count": 747,
    "top_stations": [
        {"id": "1413380", "departures_per_day": 210},
        {"id": "1413210", "departures_per_day": 64},
        {"id": "1413171", "departures_per_day": 41},
    ],
    "departures_by_hour": [
        {"hour": hour, "departures": value} for hour, value in enumerate(_HOURLY_VALUES)
    ],
}
