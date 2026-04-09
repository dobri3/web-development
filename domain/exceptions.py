from rest_framework import status
from rest_framework.exceptions import APIException

class DomainError(Exception):
    """Базовое доменное исключение"""
    status_code = 400
    error_code = "DOMAIN_ERROR"


class MovieNotFound(DomainError):
    """Фильм не найден"""
    status_code = 404
    error_code = "MOVIE_NOT_FOUND"
    
    def __init__(self, movie_id: int):
        self.movie_id = movie_id
        super().__init__(f"Movie with id {movie_id} not found")

class InvalidMovieData(DomainError):
    """Некорректные Meta данные"""
    status_code = 400
    error_code = "INVALID_MOVIE_DATA"
    
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"Incorrect data for field {field}")


class AlreadyInWatchlist(DomainError):
    """Фильм уже в watchlist"""
    status_code = 409
    error_code = "ALREADY_IN_WATCHLIST"
    
    def __init__(self, movie_id: int, username: str):
        self.movie_id = movie_id
        self.username = username
        super().__init__(f"Movie with id {movie_id} is already in {username}'s watchlist")

class WatchlistItemNotFound(DomainError):
    """Запись в watchlist не найдена"""
    status_code = 404
    error_code = "WATCHLIST_ITEM_NOT_FOUND"

    def __init__(self, movie_id: int, username: str):
        self.movie_id = movie_id
        self.username = username
        super().__init__(f"Movie with id {movie_id} is not in {username}'s watchlist")

class WatchlistLimitExceededError(DomainError):
    """Превышен лимит фильмов в watchlist"""
    status_code = 400
    error_code = "WATCHLIST_LIMIT_EXCEEDED"
    
    def __init__(self, limit: int = 100):
        self.limit = limit
        super().__init__(f"Watchlist cannot contain more than {limit} movies")


class UserNotAuthorized(DomainError):
    """Пользователь не авторизован"""
    status_code = 401
    error_code = "USER_NOT_AUTHORIZED"
    
    def __init__(self):
        super().__init__("User is not authorized")

class PermissionDenied(DomainError):
    """Нет прав доступа"""
    status_code = 403
    error_code = "PERMISSION_DENIED"
    
    def __init__(self, message: str = "You don't have access rights"):
        self.message = message
        super().__init__(message)


class GenreNotFoundError(DomainError):
    """Жанр не найден"""
    status_code = 404
    error_code = "GENRE_NOT_FOUND"
    
    def __init__(self, genre_id: int = None, genre_name: str = None):
        self.genre_id = genre_id
        self.genre_name = genre_name
        if genre_id:
            super().__init__(f"Genre with id {genre_id} not found")
        elif genre_name:
            super().__init__(f"Genre '{genre_name}' not found")
        else:
            super().__init__("Genre not found")