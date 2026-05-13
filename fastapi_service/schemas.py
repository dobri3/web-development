from pydantic import BaseModel, EmailStr


class MovieOut(BaseModel):
    id: int
    title: str
    genres: list[str]


class RecommendationRequest(BaseModel):
    user_id: int
    limit: int


class RecommendationResponse(BaseModel):
    movies: list[MovieOut]


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class MovieDetailOut(MovieOut):
    description: str | None = None
    release_year: int | None = None

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class WatchlistAddRequest(BaseModel):
    movie_id: int

class WatchlistNotifyRequest(BaseModel):
    user_id: int
    movie_id: int