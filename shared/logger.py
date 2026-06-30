from loguru import logger
import sys

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    level="INFO"
)

logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    compression="zip",      
    format="{time} | {level} | {name} - {message}",
    level="DEBUG"
)

def get_logger(name: str = "app"):
    """Получение логгера с именем модуля"""

    return logger.bind(name=name)