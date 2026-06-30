from aiohttp import web

from inventory_api.database import get_db, close_db
from inventory_api.config import config
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
    
    app.on_shutdown.append(close_all)
    
    return app

async def close_all(app: web.Application) -> None:
    await close_db()
    await close_redis()
    logger.info("Все остановлено")


async def startup() -> None:
    """Инициализация при запуске"""

    await get_db()
    logger.info("База данных инициализирована")

    await get_redis()
    logger.info("Redis запущен")


def main():
    """Точка входа для uvicorn"""

    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(startup())
    
    app = create_app()
    return app


app = main()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "inventory_api.app:app",
        host=config.host,
        port=config.port,
        log_level="info"
    )