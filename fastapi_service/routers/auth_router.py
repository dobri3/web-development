from fastapi import APIRouter, HTTPException, status
from schemas import RegisterRequest, LoginRequest, TokenResponse
from auth import hash_password, verify_password, create_access_token, create_refresh_token
from database import fake_users_db
import logging

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest):
    if data.email in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    fake_users_db[data.email] = {
        "email": data.email,
        "hashed_password": hash_password(data.password)
    }

    logger.info(f"Новый пользователь зарегистрирован: {data.email}")
    return {"message": "Регистрация успешна"}


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    user = fake_users_db.get(data.email)

    if not user or not verify_password(data.password, user["hashed_password"]):
        logger.warning(f"Неудачная попытка входа: {data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )

    logger.info(f"Пользователь вошёл: {data.email}")
    return TokenResponse(
        access_token=create_access_token(data.email),
        refresh_token=create_refresh_token(data.email)
    )