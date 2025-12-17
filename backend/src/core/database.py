"""
ARIA Database Connections - PostgreSQL, MongoDB, Redis
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
import structlog

from .config import settings

logger = structlog.get_logger()

# ============== SQLAlchemy Base ==============
Base = declarative_base()

# ============== PostgreSQL ==============

_engine = None
_async_session = None


def get_postgres_engine():
    """Get or create PostgreSQL engine"""
    global _engine
    if _engine is None:
        # Convert postgres:// to postgresql+asyncpg://
        db_url = settings.POSTGRES_URL
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        _engine = create_async_engine(
            db_url,
            echo=settings.DEBUG,
            pool_size=5,
            max_overflow=10
        )
    return _engine


def get_async_session():
    """Get async session maker"""
    global _async_session
    if _async_session is None:
        engine = get_postgres_engine()
        _async_session = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _async_session


async def get_db_session() -> AsyncSession:
    """Dependency for getting database session"""
    session_maker = get_async_session()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ============== MongoDB ==============

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls):
        """Connect to MongoDB"""
        if settings.MONGODB_URL:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            logger.info("MongoDB connected", database=settings.MONGODB_DB_NAME)
        else:
            logger.warning("MongoDB URL not configured")
    
    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB disconnected")
    
    @classmethod
    def get_collection(cls, name: str):
        """Get MongoDB collection"""
        if cls.db is None:
            raise Exception("MongoDB not connected")
        return cls.db[name]


# ============== Redis ==============

class RedisClient:
    client: Redis = None

    @classmethod
    async def connect(cls):
        """Connect to Redis"""
        if settings.REDIS_URL:
            cls.client = Redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await cls.client.ping()
            logger.info("Redis connected")
        else:
            logger.warning("Redis URL not configured")
    
    @classmethod
    async def disconnect(cls):
        """Disconnect from Redis"""
        if cls.client:
            await cls.client.close()
            logger.info("Redis disconnected")
    
    @classmethod
    def get_client(cls) -> Redis:
        """Get Redis client"""
        if cls.client is None:
            raise Exception("Redis not connected")
        return cls.client


# ============== Lifecycle ==============

async def init_databases():
    """Initialize all database connections"""
    try:
        await MongoDB.connect()
        await RedisClient.connect()
        logger.info("All databases initialized")
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        raise


async def close_databases():
    """Close all database connections"""
    await MongoDB.disconnect()
    await RedisClient.disconnect()
    logger.info("All databases closed")