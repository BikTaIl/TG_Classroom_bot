from infra.init_db import engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession
)