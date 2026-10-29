import datetime as dt
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.defaults import LOCAL_TIMEZONE, default_departures_date
from app.geo import haversine_m
from app.gtfs_time import TIME_PATTERN, time_to_seconds
from app.sample_data import DEPARTURES, STATIONS
from app.schemas import (
    Departure,
    DeparturesResponse,
    PointGeometry,
    StationCollection,
    StationFeature,
    StationProperties,
    StationRef,
)

router = APIRouter(prefix="/stations", tags=["stations"])


def _to_feature(station: dict, distance_m: float | None = None) -> StationFeature:
    return StationFeature(
        geometry=PointGeometry(coordinates=[station["lon"], station["lat"]]),
        properties=StationProperties(
            id=station["id"],
            name=station["name"],
            is_domestic=station["is_domestic"],
            distance_m=distance_m,
        ),
    )


def _find_station(station_id: str) -> dict | None:
    return next((s for s in STATIONS if s["id"] == station_id), None)


def _line(departure: dict) -> str:
    """route_short_name, a gdy pusty - route_long_name (nigdy puste)."""
    short = (departure.get("route_short_name") or "").strip()
    return short or departure["route_long_name"]


@router.get("", response_model=StationCollection, response_model_exclude_none=True)
def list_stations() -> StationCollection:
    return StationCollection(features=[_to_feature(s) for s in STATIONS])


@router.get(
    "/nearest", response_model=StationCollection, response_model_exclude_none=True
)
def nearest_stations(
    lat: float = Query(ge=-90, le=90),
    lon: float = Query(ge=-180, le=180),
    limit: int = Query(default=5, ge=1, le=50),
) -> StationCollection:
    with_distance = [
        (s, round(haversine_m(lat, lon, s["lat"], s["lon"]), 0)) for s in STATIONS
    ]
    with_distance.sort(key=lambda pair: pair[1])
    return StationCollection(
        features=[_to_feature(s, distance) for s, distance in with_distance[:limit]]
    )


@router.get("/{station_id}/departures", response_model=DeparturesResponse)
def station_departures(
    station_id: str,
    date: dt.date | None = Query(default=None),
    time: str | None = Query(default=None, pattern=TIME_PATTERN),
    limit: int = Query(default=10, ge=1, le=100),
) -> DeparturesResponse:
    station = _find_station(station_id)
    if station is None:
        raise HTTPException(status_code=404, detail="Nie ma takiej stacji")

    if date is None:
        date = default_departures_date()
    if time is None:
        time = datetime.now(LOCAL_TIMEZONE).strftime("%H:%M:%S")
    start_seconds = time_to_seconds(time)

    # Dane przykładowe nie zależą od daty; prawdziwa baza filtruje po service_date.
    upcoming = [
        d
        for d in DEPARTURES.get(station_id, [])
        if time_to_seconds(d["departure_time"]) >= start_seconds
    ]
    upcoming.sort(key=lambda d: time_to_seconds(d["departure_time"]))
    return DeparturesResponse(
        station=StationRef(id=station["id"], name=station["name"]),
        date=date,
        departures=[
            Departure(
                departure_time=d["departure_time"],
                line=_line(d),
                headsign=d["headsign"],
                trip_id=d["trip_id"],
            )
            for d in upcoming[:limit]
        ],
    )
