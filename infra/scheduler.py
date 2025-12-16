# удалять неактульные стейты из OauthState

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from commands.sync import sync_function
from commands.sync import get_students_nearing_deadline
from commands.sync import delete_overdued_states
from models.gh_client import GitHubClassroomClient
from models.db import ErrorLog, Assistant, Assignment, User, Notification, Submission, GitOrganization, Course
from db import AsyncSessionLocal
from telegram.app import bot
from telegram.keyboards.common_keyboards import return_to_the_start

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
    async with AsyncSessionLocal() as session:
        res: set[tuple[int, str, str, str]] = await get_students_nearing_deadline(session)
        for item in res:
            message: str = f"Дедлайн по заданию {item[2]} в курсе {item[1]} наступит через {item[3]} часов"
            await bot.send_message(item[0], message, reply_markup=return_to_the_start())
    async with AsyncSessionLocal() as session:
        await delete_overdued_states(session)



scheduler.add_job(check_github, IntervalTrigger(hours=8))
scheduler.add_job(check_internal_tables, IntervalTrigger(minutes=15))


async def run_scheduler():
    await check_internal_tables()
    scheduler.start()
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(run_scheduler())
