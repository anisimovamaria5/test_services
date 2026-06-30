import aioredis

from inventory_api.config import config
from shared.logger import get_logger

logger = get_logger(__name__)

_redis = None


async def get_redis() -> None:
    """Инициализация Redis"""

    global _redis
    try:
        _redis = await aioredis.from_url(
            config.redis_url,
            decode_responses=True, 
            max_connections=10
        )
        logger.info("Redis инициализирован")
    except Exception as e:
        logger.error(f"Ошибка в инициализации Redis: {e}")
        raise
    

async def close_redis():
    """Закрытие соединения при завершении"""

    global _redis
    if _redis:
        await _redis.close()
        _redis = None
        logger.info("Redis закрыт")


async def publish_event(channel: str, message: str) -> None:
    """Публикация события в Redis"""

    if _redis is None:
        raise RuntimeError("Redis не инициализирован")
    try:
        await _redis.publish(channel, message)
        logger.debug(f"Опубликовано в {channel}")
    except Exception as e:
        logger.error(f"Не удалось опубликовать в {channel}: {e}")
        raise