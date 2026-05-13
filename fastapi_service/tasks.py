import logging

logger = logging.getLogger(__name__)

def notify_user(user_email: str, movie_id: int):
    logger.info(f"[background] Начало уведомления: {user_email}, фильм {movie_id}")
    logger.info(f"[background] Уведомление отправлено: {user_email}")