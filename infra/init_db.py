from sqlalchemy.ext.asyncio import create_async_engine

import asyncio
from models.db import *
from infra.config import DATABASE_URL

engine = create_async_engine(
    DATABASE_URL
)

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
async def main():
    await init_db()


if __name__ == '__main__':
    asyncio.run(main())