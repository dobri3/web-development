from fastapi import APIRouter, Depends, HTTPException, status, Header
from app.core.auth import get_current_user
from app.services.django_client import get_django_client, DjangoAPIClient
from app.models.user import User
from app.core.config import settings
import logging

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])
logger = logging.getLogger(__name__)


async def verify_service_token(
    x_service_token: str = Header(..., alias="X-Service-Token")
):
    if x_service_token != settings.WATCHLIST_SERVICE_TOKEN:
        logger.warning(f"Invalid service token attempt")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid service token"
        )
    return True


@router.get("/")
async def get_watchlist(
    current_user: User = Depends(get_current_user),
    django_client: DjangoAPIClient = Depends(get_django_client)
):
    try:
        watchlist_data = await django_client.get_watchlist(
            current_user.id,
            token=current_user.access_token
        )
        
        logger.info(f"User {current_user.email} accessed watchlist")
        return {
            "user_id": current_user.id,
            "email": current_user.email,
            "watchlist": watchlist_data
        }
        
    except Exception as e:
        logger.error(f"Error getting watchlist for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Django service unavailable: {str(e)}"
        )


@router.post("/notify")
async def notify_watchlist_change(
    notification: dict,
    _: bool = Depends(verify_service_token)
):
    logger.info(f"Received watchlist notification: {notification}")
    return {"message": "Notification received", "data": notification}