import httpx


DJANGO_BASE_URL = "http://localhost:8000"


async def check_movie_exists(movie_id):

    async with httpx.AsyncClient(timeout=5.0) as client:

        response = await client.get(
            f"{DJANGO_BASE_URL}/api/movies/{movie_id}/"
        )

        return response.status_code == 200