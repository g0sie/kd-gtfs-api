"""Dane przykładowe do czasu podpięcia prawdziwej bazy PostGIS.

Współrzędne są przybliżone i służą tylko do testów kontraktu API.
"""

STATIONS = [
    {"id": "1", "name": "Wrocław Główny", "lon": 17.0366, "lat": 51.0985},
    {"id": "2", "name": "Legnica", "lon": 16.1546, "lat": 51.2175},
    {"id": "3", "name": "Wałbrzych Główny", "lon": 16.2835, "lat": 50.7716},
    {"id": "4", "name": "Jelenia Góra", "lon": 15.7367, "lat": 50.9013},
    {"id": "5", "name": "Kłodzko Główne", "lon": 16.6590, "lat": 50.4375},
]

DEPARTURES = {
    "1": [
        {"departure_time": "05:10:00", "line": "D1", "headsign": "Jelenia Góra", "trip_id": "D1_0001"},
        {"departure_time": "08:12:00", "line": "D1", "headsign": "Jelenia Góra", "trip_id": "D1_0002"},
        {"departure_time": "09:30:00", "line": "D3", "headsign": "Kłodzko Główne", "trip_id": "D3_0001"},
        {"departure_time": "17:45:00", "line": "D2", "headsign": "Legnica", "trip_id": "D2_0001"},
        {"departure_time": "24:35:00", "line": "D2", "headsign": "Legnica", "trip_id": "D2_0002"},
    ],
    "2": [
        {"departure_time": "06:05:00", "line": "D2", "headsign": "Wrocław Główny", "trip_id": "D2_0003"},
        {"departure_time": "18:20:00", "line": "D2", "headsign": "Wrocław Główny", "trip_id": "D2_0004"},
    ],
    "3": [
        {"departure_time": "07:40:00", "line": "D4", "headsign": "Wrocław Główny", "trip_id": "D4_0001"},
    ],
    "4": [
        {"departure_time": "06:50:00", "line": "D1", "headsign": "Wrocław Główny", "trip_id": "D1_0003"},
    ],
    "5": [
        {"departure_time": "10:15:00", "line": "D3", "headsign": "Wrocław Główny", "trip_id": "D3_0002"},
    ],
}

SEGMENTS = [
    {"from_id": "1", "to_id": "2", "trips_per_day": 38},
    {"from_id": "1", "to_id": "3", "trips_per_day": 24},
    {"from_id": "3", "to_id": "4", "trips_per_day": 12},
    {"from_id": "1", "to_id": "5", "trips_per_day": 16},
]

STATS = {
    "trips_count": 1904,
    "top_stations": [
        {"id": "1", "departures_per_day": 210},
        {"id": "2", "departures_per_day": 96},
        {"id": "3", "departures_per_day": 64},
    ],
    "departures_by_hour": [
        {"hour": 5, "departures": 12},
        {"hour": 6, "departures": 30},
        {"hour": 7, "departures": 41},
        {"hour": 8, "departures": 28},
    ],
}
