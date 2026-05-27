import logging

logger = logging.getLogger(__name__)

def notify_user(user_id: int, movie_id: int):
    try:
        logger.info(f"[background] Начало уведомления: user={user_id}, movie={movie_id}")
        logger.info(f"[background] Уведомление отправлено: user={user_id}, movie={movie_id}")
    except Exception as e:
        logger.error(f"Ошибка сервиса уведомлений: {e}")