import ssl

from app import config
from app.database.schema.schema import Base
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = config.DATABASE_URL


# Add this at the end of the file
def init_db() -> sessionmaker:
    engine = create_engine(DATABASE_URL.replace("+asyncpg", ""))
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


if config.USE_SSL:
    # Create an SSL context if SSL is required
    ssl_context = ssl.create_default_context()
    # Optional: Do not verify the server certificate (not recommended for production)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"ssl": ssl_context},
        pool_size=20,  # Maximum number of persistent connections
        max_overflow=10,  # Maximum number of additional connections created
        pool_timeout=30,  # Seconds to wait before timing out on getting a connection
        pool_recycle=1800,  # Recycle connections after 30 minutes
        pool_pre_ping=True,  # Enable connection health checks
    )
else:
    # Create the async engine without SSL configuration
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=20,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
    )

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
