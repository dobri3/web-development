from fastapi import APIRouter, BackgroundTasks, Depends
from schemas import WatchlistAddRequest
from auth import get_current_user
from tasks import notify_user
import logging
from schemas import WatchlistAddRequest, WatchlistNotifyRequest
from models.user import User

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])
logger = logging.getLogger(__name__)

@router.post("/")
async def add_to_watchlist(
    data: WatchlistAddRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    background_tasks.add_task(notify_user, current_user.email, data.movie_id)

    logger.info(f"{current_user.email} добавил фильм {data.movie_id} в вотчлист")
    return {"status": "added", "movie_id": data.movie_id}


@router.post("/notify")
async def notify(data: WatchlistNotifyRequest):
    logger.info(f"[notify] Django сообщил: user={data.user_id}, movie={data.movie_id}")
    return {"status": "received"}