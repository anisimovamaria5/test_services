import os
from pydantic import BaseModel, Field, PostgresDsn, RedisDsn


class Config(BaseModel):
    """Конфигурация приложения"""
    
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/inventory",
        description="URL подключения к PostgreSQL"
    )
    
    redis_url: RedisDsn = Field(
        default="redis://localhost:6379",
        description="URL подключения к Redis"
    )
    
    host: str = Field(
        default="0.0.0.0",
        description="Хост для запуска API"
    )
    
    port: int = Field(
        default=8080,
        ge=1,
        le=65535,
        description="Порт для запуска API"
    )
    
    log_level: str = Field(
        default="INFO",
        description="Уровень логирования"
    )


class Channels:
    """Названия каналов Redis"""
    
    RECEIPT = 'inventory.receipt'
    ISSUE = 'inventory.issue'


def load_config() -> Config:
    """Загрузка конфигурации из переменных окружения"""
    
    return Config(
        database_url=os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/inventory'),
        redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379'),
        host=os.getenv('API_HOST', '0.0.0.0'),
        port=int(os.getenv('API_PORT', '8080')),
        log_level=os.getenv('LOG_LEVEL', 'INFO'),
    )


config = load_config()