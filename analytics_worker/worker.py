import asyncio

from shared.database import check_db_connection, close_db
from analytics_worker.redis_pub import run_worker

from shared.logger import get_logger

logger = get_logger(__name__)


async def main():
    """Основная функция запуска воркера"""
    try:
        if not await check_db_connection():
            logger.error("БД недоступна!")
            raise RuntimeError("Database connection failed")

        await run_worker()
        
    except KeyboardInterrupt:
        logger.info("Worker остановлен пользователем")
    except Exception as e:
        logger.error(f"Worker не работает: {e}", exc_info=True)
    finally:
        await close_db()
        logger.info("Worker: Соединения закрыты")


if __name__ == '__main__':
    asyncio.run(main())
