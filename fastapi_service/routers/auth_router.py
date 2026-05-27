from fastapi import APIRouter, HTTPException, status
from schemas import RegisterRequest, LoginRequest
from auth import hash_password, verify_password, create_access_token, create_refresh_token
from database import fake_users_db
from schemas import RefreshRequest
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM
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
        "id": len(fake_users_db) + 1,
        "email": data.email,
        "hashed_password": hash_password(data.password),
        "role": "user"
    }

    logger.info(f"Новый пользователь зарегистрирован: {data.email}")
    
    return {
        "success": True,
        "data": {
            "message": "Регистрация успешна"
        }
    }


@router.post("/login")
async def login(data: LoginRequest):
    user = fake_users_db.get(data.email)

    if not user or not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )

    access_token = create_access_token(
        data.email,
        user_id=user["id"],
        role=user.get("role", "user")
    )

    refresh_token = create_refresh_token(data.email)

    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    }


@router.post("/refresh")
async def refresh_token(data: RefreshRequest):
    try:
        payload = jwt.decode(
            data.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")
        token_type = payload.get("type")

        if email is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидный refresh token"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный refresh token"
        )

    user = fake_users_db.get(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )

    return {
        "success": True,
        "data": {
            "access_token": create_access_token(
                email,
                user_id=user["id"],
                role=user.get("role", "user")
            ),
            "refresh_token": data.refresh_token,
            "token_type": "bearer"
        }
    }