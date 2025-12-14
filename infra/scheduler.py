# удалять неактульные стейты из OauthState

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from commands.sync import sync_function
from models.gh_client import GitHubClassroomClient
from models.db import ErrorLog
from db import AsyncSessionLocal

scheduler = AsyncIOScheduler()
gh = GitHubClassroomClient()


async def check_github():
    try:
        async with AsyncSessionLocal() as session:
            await sync_function(session)
    except Exception as e:
        async with AsyncSessionLocal() as error:
            async with error.begin():
                error.add(ErrorLog(
                    message=str(e)
                ))


async def check_internal_tables():
    pass


scheduler.add_job(check_github, IntervalTrigger(hours=8))
scheduler.add_job(check_internal_tables, IntervalTrigger(minutes=15))


async def main():
    scheduler.start()
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
