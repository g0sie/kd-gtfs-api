import datetime as dt

from fastapi import APIRouter, Query

from app import db
from app.defaults import REFERENCE_DATE
from app.schemas import (
    LineGeometry,
    SegmentCollection,
    SegmentFeature,
    SegmentProperties,
)

router = APIRouter(prefix="/segments", tags=["segments"])


def segment_feature(row: dict) -> SegmentFeature:
    return SegmentFeature(
        geometry=LineGeometry(
            coordinates=[
                [row["from_lon"], row["from_lat"]],
                [row["to_lon"], row["to_lat"]],
            ]
        ),
        properties=SegmentProperties(
            from_station_id=row["from_station_id"],
            from_station_name=row["from_station_name"],
            to_station_id=row["to_station_id"],
            to_station_name=row["to_station_name"],
            trips_per_day=row["trips_per_day"],
        ),
    )


@router.get("", response_model=SegmentCollection)
def list_segments(date: dt.date = Query(default=REFERENCE_DATE)) -> SegmentCollection:
    features = [segment_feature(row) for row in db.segments_on_date(date)]
    return SegmentCollection(date=date, features=features)