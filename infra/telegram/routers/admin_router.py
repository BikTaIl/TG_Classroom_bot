import asyncio
from pyexpat.errors import messages

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, types, Router, F
from infra.db import AsyncSessionLocal
from infra.telegram.keyboards.admin_keyboards import get_menu
from .states import *
from commands.admin_commands import *

admin_router = Router()

@admin_router.message(Command("start_admin"))
async def admin_panel(message: Message):
    await message.answer("Панель администратора:", reply_markup=get_menu())

#Команда добаволения учителя
@admin_router.callback_query(F.data == "admin_manage_users")
async def process_grant_teacher_role_first(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AddTeacher.waiting_username)
    await cb.message.answer(
        "Пришли tg username учителя в формате @username (или просто username)."
    )
    await cb.answer()

@admin_router.message(AddTeacher.waiting_username)
async def process_grant_teacher_role_second(message: Message, state: FSMContext):
    username = message.text
    await grant_teacher_role(message.from_user.id, username, AsyncSessionLocal)
    await message.answer("Учитель добавлен!")
    await state.clear()

#Команда удаления учителя
@admin_router.callback_query(F.data == "revoke_teacher_role")
async def process_revoke_teacher_role_first(cb: CallbackQuery, state: FSMContext):
    await state.set_state(RemoveTeacher.waiting_username)
    await cb.message.answer(
        "Пришли tg username учителя в формате @username (или просто username)."
    )
    await cb.answer()

@admin_router.message(RemoveTeacher.waiting_username)
async def process_revoke_teacher_role_second(message: Message, state: FSMContext):
    username = message.text
    await revoke_teacher_role(message.from_user.id, username, AsyncSessionLocal)
    await message.answer("Учитель удален!")
    await state.clear()

#Команда бана
@admin_router.callback_query(F.data == "ban_user")
async def process_ban_user_first(cb: CallbackQuery, state: FSMContext):
    await state.set_state(Ban.waiting_username)
    await cb.message.answer(
        "Пришли tg username пользователя в формате @username (или просто username)."
    )
    await cb.answer()

@admin_router.message(Ban.waiting_username)
async def process_ban_user_second(message: Message, state: FSMContext):
    username = message.text
    await ban_user(message.from_user.id, username, AsyncSessionLocal)
    await message.answer("Пользователь забанен!")
    await state.clear()

#Команда разбана
@admin_router.callback_query(F.data == "unban_user")
async def process_unban_user_first(cb: CallbackQuery, state: FSMContext):
    await state.set_state(Unban.waiting_username)
    await cb.message.answer(
        "Пришли tg username пользователя в формате @username (или просто username)."
    )
    await cb.answer()

@admin_router.message(Unban.waiting_username)
async def process_unban_user_second(message: Message, state: FSMContext):
    username = message.text
    await unban_user(message.from_user.id, username, AsyncSessionLocal)
    await message.answer("Пользователь разбанен!")
    await state.clear()


#Команда свода ошибок
@admin_router.callback_query(F.data == "unban_user")
async def process_unban_user_first(cb: CallbackQuery, state: FSMContext):
    await state.set_state(FindErrors.waiting_date)
    await cb.message.answer(
        "Пришли дату, для которой хочешь узнать сводку, или напиши '-' для общей сводки"
    )
    await cb.answer()

@admin_router.message(FindErrors.waiting_date)
async def process_unban_user_second(message: Message, state: FSMContext):
    target_date: str = message.text
    if target_date != "-":
        await get_error_count_for_day(message.from_user.id, AsyncSessionLocal, date(target_date))
    else:
        await get_error_count_for_day(message.from_user.id, AsyncSessionLocal)
    await message.answer("Пользователь разбанен!")
    await state.clear()

#Команда поиска последнего успешного запроса
@admin_router.callback_query(F.data == "get_last_successful_github_call_time")
async def process_get_last_successful_github_call_time(cb: CallbackQuery, state: FSMContext):
    answer = await get_last_successful_github_call_time(cb.message.from_user.id, AsyncSessionLocal)
    if answer:
        await cb.message.answer(f"Последнее успешное обращение к GitHub было {answer}")
    else:
        await cb.message.answer("Успешных обращений к GitHub не было")

#Команда свода ошибок
@admin_router.callback_query(F.data == "get_last_failed_github_call_info")
async def process_get_last_failed_github_call_info(cb: CallbackQuery, state: FSMContext):
    answer = await get_last_failed_github_call_info(cb.message.from_user.id, AsyncSessionLocal)
    if answer:
        await cb.message.answer(f"Информация о последнем ошибочном обращении к GitHub: {answer}")
    else:
        await cb.message.answer("Ошибочных обращений к GitHub не было")