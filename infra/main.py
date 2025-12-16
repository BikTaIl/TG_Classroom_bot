import asyncio

from telegram.app import run_bot
from scheduler import run_scheduler
from git.router import start_fastapi
from init_db import init_db

async def main():
    await asyncio.gather(init_db(), run_bot(), start_fastapi(), run_scheduler())

if __name__ == '__main__':
    asyncio.run(main())