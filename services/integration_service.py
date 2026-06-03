import httpx
from django.conf import settings


DJANGO_BASE_URL = "http://localhost:8000"


async def check_movie_exists(movie_id):

    async with httpx.AsyncClient(timeout=5.0) as client:

        response = await client.get(
            f"{DJANGO_BASE_URL}/api/movies/{movie_id}/"
        )

        return response.status_code == 200


def notify_fastapi_watchlist_added(user_id: int, movie_id: int):
    """Notify FastAPI service that a movie was added to a watchlist.

    Kept as a small integration wrapper so tests and service code can patch the
    external boundary without touching domain logic.
    """
    return httpx.post(
        f"{settings.FASTAPI_SERVICE_URL}/watchlist/notify",
        json={"user_id": user_id, "movie_id": movie_id},
        timeout=2.0,
    )
