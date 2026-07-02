from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from shared.config import config
from shared.logger import get_logger

logger = get_logger(__name__)

async_engine = create_async_engine(
    str(config.database_url), 
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600
)


async def check_db_connection() -> bool:
    """Проверка доступности БД"""
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("База данных доступна")
            return True
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        return False


async def close_db() -> None:
    """Закрытие базы данных"""

    await async_engine.dispose()
    logger.info("База данных закрыта")