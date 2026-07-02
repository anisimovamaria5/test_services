from aiohttp import web

from shared.database import check_db_connection, close_db
from shared.config import config
from inventory_api.handlers import Handlers
from inventory_api.redis_pub import get_redis, close_redis

from shared.logger import get_logger

logger = get_logger(__name__)

def create_app() -> web.Application:
    """Создание и настройка приложения"""

    app = web.Application()
    
    handler = Handlers()
    app.router.add_post('/receipts', handler.post_receipts)
    app.router.add_post('/issues', handler.post_issues)
    app.router.add_get('/stock', handler.get_stock)
    app.router.add_get('/stock/summary', handler.get_stock_summary)
    
    app.on_startup.append(startup)
    app.on_shutdown.append(shutdown)
    
    return app

async def startup(app: web.Application) -> None:
    """Инициализация при запуске"""
    
    if not await check_db_connection():
        logger.error("БД недоступна!")
        raise RuntimeError("Не удалось подключиться к базе данных")
    logger.info("База данных доступна")
    
    await get_redis()
    logger.info("Redis запущен")

async def shutdown(app: web.Application) -> None:
    """Завершение работы"""

    await close_db()
    await close_redis()
    logger.info("Все остановлено")

app = create_app()

if __name__ == '__main__':
    web.run_app(app, host=config.host, port=config.port)