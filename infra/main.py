import asyncio

from .telegram.app import run_bot
from infra.scheduler import run_scheduler
from .git.router import start_fastapi
from infra.init_db import init_db

async def main():
    await init_db()
    await asyncio.gather(run_bot(), start_fastapi(), run_scheduler())

if __name__ == '__main__':
    asyncio.run(main())