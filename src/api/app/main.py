from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, segments, stations, stats

app = FastAPI(
    title="API stacji Kolei Dolnośląskich",
    description="Stacje, odjazdy, odcinki i statystyki na podstawie GTFS.",
    version="0.1.0",
)

# Front (Vite) działa na innym porcie, więc przeglądarka wymaga CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(stations.router)
app.include_router(segments.router)
app.include_router(stats.router)
