from fastapi import APIRouter, BackgroundTasks, Depends
from schemas import WatchlistAddRequest, WatchlistNotifyRequest
from auth import get_current_user
from tasks import notify_user
import logging

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])
logger = logging.getLogger(__name__)

@router.post("/")
async def add_to_watchlist(
    data: WatchlistAddRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    background_tasks.add_task(
        notify_user,
        current_user["id"],
        data.movie_id
    )

    logger.info(f"{current_user['id']} добавил фильм {data.movie_id} в вотчлист")
    return {
        "success": True,
        "data": {
            "status": "added",
            "movie_id": data.movie_id
        }
    }
