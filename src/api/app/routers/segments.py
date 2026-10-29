from fastapi import APIRouter

from app.sample_data import SEGMENTS, STATIONS
from app.schemas import (
    LineGeometry,
    SegmentCollection,
    SegmentFeature,
    SegmentProperties,
)

router = APIRouter(prefix="/segments", tags=["segments"])


@router.get("", response_model=SegmentCollection)
def list_segments() -> SegmentCollection:
    stations_by_id = {s["id"]: s for s in STATIONS}
    features = []
    for segment in SEGMENTS:
        start = stations_by_id[segment["from_id"]]
        end = stations_by_id[segment["to_id"]]
        features.append(
            SegmentFeature(
                geometry=LineGeometry(
                    coordinates=[[start["lon"], start["lat"]], [end["lon"], end["lat"]]]
                ),
                properties=SegmentProperties(
                    from_station_id=start["id"],
                    from_station_name=start["name"],
                    to_station_id=end["id"],
                    to_station_name=end["name"],
                    trips_per_day=segment["trips_per_day"],
                ),
            )
        )
    return SegmentCollection(features=features)
