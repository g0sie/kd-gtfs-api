import datetime as dt
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path, Query

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
    """Wszystkie stacje (krajowe i zagraniczne) jako GeoJSON."""
    return StationCollection(features=[_to_feature(s) for s in db.list_stations()])


@router.get(
    "/nearest", response_model=StationCollection, response_model_exclude_none=True
)
def nearest_stations(
    lat: float = Query(
        ge=-90,
        le=90,
        description="Szerokość geograficzna punktu (WGS 84).",
        openapi_examples={"wroclaw": {"summary": "Wrocław, Rynek", "value": 51.11}},
    ),
    lon: float = Query(
        ge=-180,
        le=180,
        description="Długość geograficzna punktu (WGS 84).",
        openapi_examples={"wroclaw": {"summary": "Wrocław, Rynek", "value": 17.03}},
    ),
    limit: int = Query(default=5, ge=1, le=50, description="Liczba zwracanych stacji."),
) -> StationCollection:
    """Stacje najbliższe wskazanemu punktowi z odległością w metrach (GeoJSON)."""
    # Odległość i sortowanie liczy baza (geography, docs/decisions.md)
    stations = db.nearest_stations(lat=lat, lon=lon, limit=limit)
    return StationCollection(
        features=[_to_feature(s, s["distance_m"]) for s in stations]
    )


@router.get("/{station_id}/departures", response_model=DeparturesResponse)
def station_departures(
    station_id: str = Path(
        description="Identyfikator stacji (stop_id z GTFS).",
        openapi_examples={
            "wroclaw_glowny": {"summary": "Wrocław Główny", "value": "1413380"}
        },
    ),
    date: dt.date | None = Query(
        default=None,
        description=(
            "Dzień (RRRR-MM-DD). Domyślnie dzisiaj, "
            "a poza zakresem rozkładu dzień wzorcowy."
        ),
        openapi_examples={
            "dzien_roboczy": {"summary": "Dzień roboczy", "value": "2026-11-24"}
        },
    ),
    time: str | None = Query(
        default=None,
        pattern=TIME_PATTERN,
        description=(
            "Godzina (HH:MM:SS), od której szukamy odjazdów. "
            "Domyślnie aktualna godzina."
        ),
        openapi_examples={"rano": {"summary": "8:00", "value": "08:00:00"}},
    ),
    limit: int = Query(
        default=10, ge=1, le=100, description="Liczba zwracanych odjazdów."
    ),
) -> DeparturesResponse:
    """Najbliższe odjazdy ze stacji od podanej godziny w danym dniu."""
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
