import asyncio

from sqlalchemy.ext.asyncio import create_async_engine
from inventory_api.config import config
from inventory_api.models import metadata
from shared.logger import get_logger

logger = get_logger(__name__)

async_engine = create_async_engine(
    config.database_url, 
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600
)


async def get_db() -> None:
    """Инициализация базы данных"""
    
    max_retries = 10
    retry_delay = 3
    
    for attempt in range(max_retries):
        try:
            async with async_engine.begin() as conn:
                await conn.run_sync(metadata.create_all)
                logger.info("База данных работает")
                return
        except Exception as e:
            logger.info(f"Не удалось подключиться к базе данных {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                raise


async def close_db() -> None:
    """Закрытие базы данных"""

    await async_engine.dispose()