import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from infra.telegram.routers.common_router import common_router
from infra.telegram.routers.admin_router import admin_router
from infra.telegram.routers.assistant_router import assistant_router
from infra.telegram.routers.student_router import student_router
from infra.telegram.routers.teacher_router import teacher_router
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

async def run_bot():
    dp.include_router(common_router)
    dp.include_router(admin_router)
    dp.include_router(assistant_router)
    dp.include_router(student_router)
    dp.include_router(teacher_router)
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(run_bot())