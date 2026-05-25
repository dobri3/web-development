import hashlib
import secrets
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

oauth2_scheme = HTTPBearer()

def hash_password(password: str) -> str:
    salt = secrets.token_hex(32)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return f"{salt}:{key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    try:
        hash_part, salt = hashed_password.split(':')
        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return new_key.hex() == hash_part
    except Exception as e:
        print(f"DEBUG verify error: {e}")
        return False

def create_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + expires_delta
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(user: User) -> str:
    return create_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "type": "access"
        },
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

def create_refresh_token(user: User) -> str:
    return create_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "type": "refresh"
        },
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный или просроченный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise credentials_error

    except JWTError:
        raise credentials_error

    result = await db.execute(
        select(User).where(User.id == int(user_id))
    )
    
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_error

    return user