# fastapi_service/auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + expires_delta
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(
        email: str,
        user_id: int,
        role: str = "user"
    ) -> str:

    return create_token(
        {
            "sub": email,
            "user_id": user_id,
            "role": role,
            "type": "access",
        },
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

def create_refresh_token(email: str, user_id: int) -> str:
    return create_token(
        {"sub": email, "user_id": user_id, "type": "refresh"},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> dict:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный или просроченный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials  # вытаскиваем токен из объекта
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")

        if email is None or token_type != "access":
            raise credentials_error

    except JWTError:
        logger.info(f"Invalid JWT token")
        raise credentials_error

    user_id = payload.get("user_id")
    role = payload.get("role")

    if user_id is None or email is None:
        logger.warning(f"Invalid JWT payload: {payload}")
        raise credentials_error

    return {
        "id": user_id,
        "email": email,
        "role": role
    }