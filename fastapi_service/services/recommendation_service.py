from schemas import MovieOut


def build_recommendations(
    movies: list[dict],
    user_id: int,
    limit: int,
) -> list[MovieOut]:
    """
    Простая учебная логика рекомендаций.

    Пока нет ML и истории просмотров, делаем детерминированную выдачу:
    для разных user_id список начинается с разных фильмов.
    """
    if not movies:
        return []

    offset = user_id % len(movies)
    ordered_movies = movies[offset:] + movies[:offset]

    return [MovieOut(**movie) for movie in ordered_movies[:limit]]