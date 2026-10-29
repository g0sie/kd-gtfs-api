"""Dane przykładowe do czasu podpięcia prawdziwej bazy (tydzień 3).

Nie zależą od daty: każda data zwraca te same wartości.
"""

STATIONS = [
    {"id": "1413380", "name": "Wrocław Główny", "lat": 51.0985, "lon": 17.0366, "is_domestic": True},
    {"id": "1413385", "name": "Legnica", "lat": 51.2175, "lon": 16.1546, "is_domestic": True},
    {"id": "1413405", "name": "Jelenia Góra", "lat": 50.9013, "lon": 15.7375, "is_domestic": True},
    {"id": "1413390", "name": "Görlitz", "lat": 51.1516, "lon": 14.9867, "is_domestic": False},
    {"id": "1413395", "name": "Dresden Hbf", "lat": 51.0404, "lon": 13.7320, "is_domestic": False},
    {"id": "1413400", "name": "Trutnov", "lat": 50.5610, "lon": 15.9125, "is_domestic": False},
]

SEGMENTS = [
    {"from_id": "1413380", "to_id": "1413385", "trips_per_day": 38},
    {"from_id": "1413380", "to_id": "1413405", "trips_per_day": 24},
    {"from_id": "1413385", "to_id": "1413390", "trips_per_day": 12},
    {"from_id": "1413390", "to_id": "1413395", "trips_per_day": 10},
]

# route_short_name bywa puste (7 linii ma tylko route_long_name).
DEPARTURES = {
    "1413380": [
        {"departure_time": "08:12:00", "route_short_name": "D1", "route_long_name": "Wrocław - Jelenia Góra", "headsign": "Jelenia Góra", "trip_id": "51384888_452001"},
        {"departure_time": "08:40:00", "route_short_name": "D2", "route_long_name": "Wrocław - Legnica", "headsign": "Legnica", "trip_id": "51384888_452002"},
        {"departure_time": "09:05:00", "route_short_name": "", "route_long_name": "D91/D64", "headsign": "Görlitz", "trip_id": "51384888_452003"},
        {"departure_time": "24:48:00", "route_short_name": "D1", "route_long_name": "Wrocław - Jelenia Góra", "headsign": "Jelenia Góra", "trip_id": "51384888_452004"},
    ],
    "1413385": [
        {"departure_time": "08:55:00", "route_short_name": "D2", "route_long_name": "Wrocław - Legnica", "headsign": "Wrocław Główny", "trip_id": "51384888_452005"},
    ],
}

# Zawsze 25 pozycji: 0-23 to godziny, 24 to odjazdy po północy (>= 24:00:00).
_HOURLY_VALUES = [4, 2, 0, 0, 6, 18, 42, 55, 50, 44, 38, 36, 40, 42, 46, 52, 60, 58, 48, 40, 34, 30, 24, 14, 12]

STATS = {
    "trips_count": 747,
    "top_stations": [
        {"id": "1413380", "departures_per_day": 210},
        {"id": "1413385", "departures_per_day": 64},
        {"id": "1413405", "departures_per_day": 41},
    ],
    "departures_by_hour": [
        {"hour": hour, "departures": value} for hour, value in enumerate(_HOURLY_VALUES)
    ],
}
