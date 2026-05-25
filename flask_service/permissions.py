from functools import wraps
from flask import jsonify, request, g

from auth import auth_error


def permission_error(detail: str, status_code: int = 403):
    return jsonify({
        "error": "FORBIDDEN",
        "detail": detail,
    }), status_code


def roles_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            current_user = getattr(g, "current_user", None)

            if not current_user:
                return auth_error("Authentication required")

            if current_user.get("role") not in allowed_roles:
                return permission_error(
                    "Only admin or moderator can change UGC status"
                )

            return view_func(*args, **kwargs)

        return wrapper

    return decorator