from fastapi import APIRouter

from app import db
from app.schemas import FeedResponse

router = APIRouter(tags=["feed"])


@router.get("/feed", response_model=FeedResponse)
def get_feed() -> FeedResponse:
    """Zakres obowiązywania rozkładu z kalendarza w bazie (db.feed_range())."""
    start_date, end_date = db.feed_range()
    return FeedResponse(start_date=start_date, end_date=end_date)
