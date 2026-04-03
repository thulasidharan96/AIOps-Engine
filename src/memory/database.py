from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from redis import asyncio as aioredis
from src.config.settings import settings

Base = declarative_base()

# PostgreSQL Setup
engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db_session() -> AsyncSession: # type: ignore
    async with AsyncSessionLocal() as session:
        yield session

# Redis Setup
redis_client = aioredis.from_url(
    settings.REDIS_URL, 
    decode_responses=True
)

async def get_redis() -> aioredis.Redis:
    return redis_client
