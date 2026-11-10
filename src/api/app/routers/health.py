from fastapi import APIRouter

from app import db
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """API działa zawsze (200); pole `database` mówi, czy jest połączenie z bazą."""
    database = db.check_connection()
    stations_count = db.count_stations() if database == "ok" else None
    return HealthResponse(status="ok", database=database, stations_count=stations_count)
