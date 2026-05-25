import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Optional, Dict, Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class DjangoAPIClient:
    def __init__(self):
        self.base_url = settings.DJANGO_API_URL
        self.api_key = settings.DJANGO_API_KEY
        self.timeout = httpx.Timeout(settings.HTTP_TIMEOUT)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
    
    async def close(self):
        await self.client.aclose()
    
    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    @retry(
        stop=stop_after_attempt(settings.HTTP_MAX_RETRIES),
        wait=wait_exponential(multiplier=settings.HTTP_RETRY_BACKOFF, min=1, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError))
    )
    async def get_watchlist(self, user_id: int, token: str) -> Dict[str, Any]:
        logger.info(f"Fetching watchlist for user {user_id}")
        response = await self.client.get(
            f"/watchlist/{user_id}",
            headers=self._get_headers(token)
        )
        response.raise_for_status()
        return response.json()

django_client = DjangoAPIClient()

async def get_django_client() -> DjangoAPIClient:
    return django_client