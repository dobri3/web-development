from pydantic import BaseModel


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