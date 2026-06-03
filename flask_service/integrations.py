import logging
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def check_movie_exists(movie_id: int) -> tuple[bool, bool]:
    django_url = os.getenv("DJANGO_SERVICE_URL", "http://127.0.0.1:8000").rstrip("/")
    logger.debug("checking movie %s at %s", movie_id, django_url)
    try:
        response = httpx.get(
            f"{django_url}/api/movies/{movie_id}/",
            timeout=2.0
        )
        logger.debug("response status = %s", response.status_code)

        if response.status_code == 200:
            return True, True

        if response.status_code == 404:
            return False, True

    except httpx.TimeoutException:
        logger.warning(
            "Django movie check timed out for movie_id=%s",
            movie_id,
        )
        return False, False

    except httpx.RequestError as e:
        logger.warning(f"Django недоступен, пропускаем проверку фильма: {e}")
        return False, False

    return False, False