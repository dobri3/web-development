import logging
from typing import Any

import httpx
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

DJANGO_API_BASE_URL = "http://127.0.0.1:8000/api"
DJANGO_API_TIMEOUT = 3.0


def _normalize_movie(raw: dict[str, Any]) -> dict[str, Any]:
    genres = raw.get("genres") or []

    if genres and isinstance(genres[0], dict):
        genres = [genre.get("name", str(genre)) for genre in genres]

    return {
        "id": raw.get("id"),
        "title": raw.get("title"),
        "description": raw.get("description"),
        "release_year": raw.get("release_year"),
        "genres": genres,
    }


async def fetch_movies_from_django() -> list[dict[str, Any]]:
    try:
        async with httpx.AsyncClient(
            base_url=DJANGO_API_BASE_URL,
            timeout=DJANGO_API_TIMEOUT,
        ) as client:
            response = await client.get("/movies/")
            response.raise_for_status()

    except httpx.HTTPStatusError as exc:
        logger.exception("Django API returned error while fetching movies")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ошибка при получении фильмов из Django API",
        ) from exc

    except httpx.RequestError as exc:
        logger.exception("Django API is unavailable")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Django API временно недоступен",
        ) from exc

    data = response.json()

    if isinstance(data, dict):
        raw_movies = data.get("results", [])
    else:
        raw_movies = data

    return [_normalize_movie(movie) for movie in raw_movies]


async def fetch_movie_from_django(movie_id: int) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(
            base_url=DJANGO_API_BASE_URL,
            timeout=DJANGO_API_TIMEOUT,
        ) as client:
            response = await client.get(f"/movies/{movie_id}/")

            if response.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Фильм с id={movie_id} не найден",
                )

            response.raise_for_status()

    except HTTPException:
        raise

    except httpx.HTTPStatusError as exc:
        logger.exception("Django API returned error while fetching movie")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ошибка при получении фильма из Django API",
        ) from exc

    except httpx.RequestError as exc:
        logger.exception("Django API is unavailable")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Django API временно недоступен",
        ) from exc

    return _normalize_movie(response.json())