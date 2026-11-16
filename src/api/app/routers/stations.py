import datetime as dt
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app import db
from app.defaults import LOCAL_TIMEZONE, default_departures_date
from app.gtfs_time import TIME_PATTERN, seconds_to_time, time_to_seconds
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


@router.get("", response_model=StationCollection, response_model_exclude_none=True)
def list_stations() -> StationCollection:
    return StationCollection(features=[_to_feature(s) for s in db.list_stations()])


@router.get(
    "/nearest", response_model=StationCollection, response_model_exclude_none=True
)
def nearest_stations(
    lat: float = Query(ge=-90, le=90),
    lon: float = Query(ge=-180, le=180),
    limit: int = Query(default=5, ge=1, le=50),
) -> StationCollection:
    # Odległość i sortowanie liczy baza (geography, docs/decisions.md)
    stations = db.nearest_stations(lat=lat, lon=lon, limit=limit)
    return StationCollection(
        features=[_to_feature(s, s["distance_m"]) for s in stations]
    )


@router.get("/{station_id}/departures", response_model=DeparturesResponse)
def station_departures(
    station_id: str,
    date: dt.date | None = Query(default=None),
    time: str | None = Query(default=None, pattern=TIME_PATTERN),
    limit: int = Query(default=10, ge=1, le=100),
) -> DeparturesResponse:
    station = db.get_station(station_id)
    if station is None:
        raise HTTPException(status_code=404, detail="Nie ma takiej stacji")

    if date is None:
        date = default_departures_date(*db.feed_range())
    if time is None:
        time = datetime.now(LOCAL_TIMEZONE).strftime("%H:%M:%S")

    # Sekundy doby kursu: odjazdy po północy (np. 24:48:00) są na końcu tego samego dnia
    rows = db.station_departures(
        station_id=station_id,
        service_date=date,
        start_sec=time_to_seconds(time),
        limit=limit,
    )
    return DeparturesResponse(
        station=StationRef(id=station["id"], name=station["name"]),
        date=date,
        departures=[
            Departure(
                departure_time=seconds_to_time(row["departure_sec"]),
                line=row["line"],
                headsign=row["headsign"],
                trip_id=row["trip_id"],
            )
            for row in rows
        ],
    )