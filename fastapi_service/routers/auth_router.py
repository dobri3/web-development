# auth_router.py
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse
)

from auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password
)

from database import get_db
from models.user import User

import logging

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.email == data.email)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    new_user = User(
        username=data.email,
        email=data.email,
        password=hash_password(data.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(f"Новый пользователь зарегистрирован: {data.email}")
    return {"message": "Регистрация успешна"}


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.email == data.email)
    )

    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password):
        logger.warning(f"Неудачная попытка входа: {data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )

    logger.info(f"Пользователь вошёл: {data.email}")
    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user)
    )


@router.get("/me")
async def me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username
    }