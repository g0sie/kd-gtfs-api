import datetime as dt
from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class PointGeometry(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: list[float]


class LineGeometry(BaseModel):
    type: Literal["LineString"] = "LineString"
    coordinates: list[list[float]]


class StationProperties(BaseModel):
    id: str
    name: str
    is_domestic: bool
    distance_m: float | None = None


class StationFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: PointGeometry
    properties: StationProperties


class StationCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[StationFeature]


class StationRef(BaseModel):
    id: str
    name: str


class Departure(BaseModel):
    departure_time: str
    line: str
    headsign: str
    trip_id: str


class DeparturesResponse(BaseModel):
    station: StationRef
    date: dt.date
    departures: list[Departure]


class SegmentProperties(BaseModel):
    from_station_id: str
    from_station_name: str
    to_station_id: str
    to_station_name: str
    trips_per_day: int


class SegmentFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: LineGeometry
    properties: SegmentProperties


class SegmentCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    date: dt.date
    features: list[SegmentFeature]


class TopStation(BaseModel):
    id: str
    name: str
    departures_per_day: int


class HourlyDepartures(BaseModel):
    hour: int
    departures: int


class StatsResponse(BaseModel):
    date: dt.date
    stations_count: int
    trips_count: int
    top_stations: list[TopStation]
    departures_by_hour: list[HourlyDepartures]
