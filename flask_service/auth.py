import os
from functools import wraps

from dotenv import load_dotenv
from flask import jsonify, request, g
from jose import JWTError, jwt

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


def auth_error(detail: str, status_code: int = 401):
    return jsonify({
        "error": "AUTHENTICATION_FAILED",
        "detail": detail,
    }), status_code


def get_current_user_from_token():
    if not SECRET_KEY:
        return None, auth_error("JWT secret key is not configured", 500)

    auth_header = request.headers.get("Authorization", "")

    if not auth_header:
        return None, auth_error("Authorization header is required")

    if not auth_header.startswith("Bearer "):
        return None, auth_error("Authorization header must be Bearer token")

    token = auth_header.removeprefix("Bearer ").strip()

    if not token:
        return None, auth_error("Bearer token is empty")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None, auth_error("Invalid or expired token")

    if payload.get("type") != "access":
        return None, auth_error("Only access token is allowed")

    email = payload.get("sub")
    user_id = payload.get("user_id")
    role = payload.get("role", "user")

    if not email:
        return None, auth_error("Token does not contain user email")

    if not isinstance(user_id, int) or isinstance(user_id, bool):
        return None, auth_error("Token does not contain valid user_id")

    if role not in {"user", "moderator", "admin"}:
        return None, auth_error("Token contains invalid role")

    return {
        "id": user_id,
        "email": email,
        "role": role,
    }, None

def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        current_user, error_response = get_current_user_from_token()

        if error_response:
            return error_response

        g.current_user = current_user
        return view_func(*args, **kwargs)

    return wrapper