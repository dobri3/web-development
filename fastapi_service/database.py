fake_users_db: dict = {}
_next_user_id = 1


def get_next_user_id() -> int:
    global _next_user_id

    user_id = _next_user_id
    _next_user_id += 1

    return user_id