from fastapi import APIRouter, HTTPException, status
from schemas import RegisterRequest, LoginRequest, TokenResponse
from auth import hash_password, verify_password, create_access_token, create_refresh_token
from database import fake_users_db, get_next_user_id
import os
import logging

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)

def get_role_for_email(email: str) -> str:
    user_email = email.strip().lower()

    admin_emails = {
        item.strip().lower()
        for item in os.getenv("ADMIN_EMAILS", "").split(",")
        if item.strip()
    }

    moderator_emails = {
        item.strip().lower()
        for item in os.getenv("MODERATOR_EMAILS", "").split(",")
        if item.strip()
    }

    if user_email in admin_emails:
        return "admin"

    if user_email in moderator_emails:
        return "moderator"

    return "user"

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

<<<<<<< HEAD
    new_user = User(
        username=data.email,
        email=data.email,
        password=make_password(data.password)
    )

    db.add(new_user)

    await db.commit()
=======
    role = get_role_for_email(data.email)

    fake_users_db[data.email] = {
        "id": get_next_user_id(),
        "email": data.email,
        "role": role,
        "hashed_password": hash_password(data.password)
    }
>>>>>>> fix/flask

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
<<<<<<< HEAD
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user)
=======
        access_token=create_access_token(data.email, user["id"], user.get("role", "user")),
        refresh_token=create_refresh_token(data.email, user["id"], user.get("role", "user"))
>>>>>>> fix/flask
    )