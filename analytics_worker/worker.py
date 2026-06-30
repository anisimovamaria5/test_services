import asyncio

from analytics_worker.database import close_db, get_db
from analytics_worker.redis_pub import run_worker

from shared.logger import get_logger

logger = get_logger(__name__)


async def main():
    """Основная функция запуска воркера"""
    try:
        await get_db()
        logger.info("Worker: База данных инициализирована")

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
