import datetime as dt

from fastapi import APIRouter, Query

from app import db
from app.defaults import REFERENCE_DATE
from app.schemas import HourlyDepartures, StatsResponse, TopStation

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
def get_stats(date: dt.date = Query(default=REFERENCE_DATE)) -> StatsResponse:
    # Wszystkie liczby z bazy dla dnia date (stations_count od daty nie zależy)
    stats = db.stats(date)
    return StatsResponse(
        date=date,
        stations_count=stats["stations_count"],
        trips_count=stats["trips_count"],
        top_stations=[TopStation(**station) for station in stats["top_stations"]],
        departures_by_hour=[
            HourlyDepartures(**bucket) for bucket in stats["departures_by_hour"]
        ],
    )