from fastapi import APIRouter

from app.sample_data import STATIONS, STATS
from app.schemas import StatsResponse, TopStation

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
def get_stats() -> StatsResponse:
    names_by_id = {s["id"]: s["name"] for s in STATIONS}
    top_stations = [
        TopStation(
            id=entry["id"],
            name=names_by_id[entry["id"]],
            departures_per_day=entry["departures_per_day"],
        )
        for entry in STATS["top_stations"]
    ]
    return StatsResponse(
        stations_count=len(STATIONS),
        trips_count=STATS["trips_count"],
        top_stations=top_stations,
        departures_by_hour=STATS["departures_by_hour"],
    )
