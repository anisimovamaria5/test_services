import asyncio
import json
import aioredis

from shared.config import config, Channels
from shared.database import async_engine
from analytics_worker.services.stock_aggregator import StockAggregator
from shared.logger import get_logger
from shared.schemas import EventMessage

logger = get_logger(__name__)

_redis = None
subscriber = None

aggregator = StockAggregator()

async def get_redis() -> None:
    """Инициализация Redis"""

    global _redis, subscriber
    try:
        _redis = await aioredis.from_url(
            (str(config.redis_url)),
            decode_responses=True, 
            max_connections=10
        )
        subscriber = _redis.pubsub()
        logger.info("Redis инициализирован")
    except Exception as e:
        logger.error(f"Ошибка в инициализации Redis: {e}")
        raise
    

async def close_redis() -> None:
    """Закрытие Redis"""

    global _redis, subscriber
    if subscriber:
        await subscriber.unsubscribe()
        await subscriber.close()
        subscriber = None
    if _redis:
        await _redis.close()
        _redis = None
        logger.info("Redis закрыт")


async def handle_event(message: dict) -> None:
    """Обработка полученного события (вызывает сервис)"""
    try:
        data = json.loads(message['data'])
        event = EventMessage(**data)
    except Exception as e:
        logger.error(f"Ошибка валидации события: {e}")
        return
    
    try:
        async with async_engine.begin() as conn:
            await aggregator.process_event(conn, event)
    except Exception as e:
        logger.error(f"Ошибка обработки события: {e}", exc_info=True)
        raise


async def run_worker() -> None:
    """Запуск worker"""

    await get_redis()

    await subscriber.subscribe(Channels.RECEIPT)
    await subscriber.subscribe(Channels.ISSUE)
    logger.info(f"Подписан на каналы: {Channels.RECEIPT}, {Channels.ISSUE}")
    
    try:
        async for message in subscriber.listen():
            if message['type'] == 'message':
                await handle_event(message)
            elif message['type'] == 'subscribe':
                logger.info(f"Подписан на канал: {message['channel']}")
    except asyncio.CancelledError:
        logger.info("Worker остановлен")
    finally:
        await close_redis()
