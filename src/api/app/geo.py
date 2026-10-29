"""Proste obliczenia geograficzne dla danych przykładowych.

Po podpięciu bazy odległości liczy PostGIS (ST_Distance na typie geography).
"""

from math import asin, cos, radians, sin, sqrt

EARTH_RADIUS_M = 6_371_000


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Odległość w metrach między dwoma punktami na kuli ziemskiej."""
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    return 2 * EARTH_RADIUS_M * asin(sqrt(a))
