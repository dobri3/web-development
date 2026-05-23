import logging
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def check_movie_exists(movie_id: int) -> tuple[bool, bool]:
    django_url = os.getenv("DJANGO_SERVICE_URL", "http://127.0.0.1:8000")
    print(f"DEBUG: checking movie {movie_id} at {django_url}")
    try:
        response = httpx.get(
            f"{django_url}/api/movies/{movie_id}/",
            timeout=2.0
        )
        print(f"DEBUG: response status = {response.status_code}")
        if response.status_code == 200:
            return True, True
        if response.status_code == 404:
            return False, True
        return False, True
    except httpx.RequestError as e:
        print(f"DEBUG: request error = {e}")
        logger.warning(f"Django недоступен, пропускаем проверку фильма: {e}")
        return False, False