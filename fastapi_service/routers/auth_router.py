from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
    Body
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

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
from config import SECRET_KEY, ALGORITHM

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


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный или просроченный refresh токен",
    )
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            logger.warning("Попытка использования access токена как refresh")
            raise credentials_error
            
    except JWTError as e:
        logger.warning(f"Ошибка декодирования refresh токена: {e}")
        raise credentials_error
    
    result = await db.execute(
        select(User).where(User.id == int(user_id))
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        logger.warning(f"Пользователь с id {user_id} не найден при обновлении токена")
        raise credentials_error
    
    logger.info(f"Токены обновлены для пользователя: {user.email}")
    
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