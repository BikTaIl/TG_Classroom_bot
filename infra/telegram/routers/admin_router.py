import asyncio
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F

from adapters.table_to_text import table_to_text
from infra.db import AsyncSessionLocal
from infra.telegram.keyboards.admin_keyboards import *
from .states import *
from commands.admin_commands import *

admin_router = Router()

@admin_router.callback_query(F.data == "start_admin")
async def admin_panel(cb: CallbackQuery):
    """Отображение клавиатуры админа"""
    await cb.message.answer("Панель администратора:", reply_markup=get_admin_menu())
    await cb.answer()

@admin_router.callback_query(F.data == "grant_teacher_role")
async def process_grant_teacher_role_first(cb: CallbackQuery, state: FSMContext):
    """Дать роль учителя пользователю"""
    await state.set_state(AddTeacher.waiting_username)
    await cb.message.answer(
        "Пришли tg username учителя в формате @username (или просто username)."
    )
    await cb.answer()

@admin_router.message(AddTeacher.waiting_username)
async def process_grant_teacher_role_second(message: Message, state: FSMContext):
    """Ввод ника пользователя, которому даются права учителя"""
    username = message.text
    async with AsyncSessionLocal() as session:
        await grant_teacher_role(message.from_user.id, username, session)
    await message.answer("Учитель добавлен!", reply_markup=return_to_the_menu())
    await state.clear()


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
    async with AsyncSessionLocal() as session:
        await revoke_teacher_role(message.from_user.id, username, session)
    await message.answer("Учитель удален!", reply_markup=return_to_the_menu())
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
    async with AsyncSessionLocal() as session:
        await ban_user(message.from_user.id, username, session)
    await message.answer("Пользователь забанен!", reply_markup=return_to_the_menu())
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
    async with AsyncSessionLocal() as session:
        await unban_user(message.from_user.id, username, session)
    await message.answer("Пользователь разбанен!", reply_markup=return_to_the_menu())
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
    async with AsyncSessionLocal() as session:
        if target_date != "-":
            result = await get_error_count_for_day(message.from_user.id, session, date(target_date))
        else:
            result = await get_error_count_for_day(message.from_user.id, session)
    await message.answer(f"Ошибок за указанный период: {result}", reply_markup=return_to_the_menu())
    await state.clear()

#Команда поиска последнего успешного запроса
@admin_router.callback_query(F.data == "get_last_successful_github_call_time")
async def process_get_last_successful_github_call_time(cb: CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as session:
        answer = await get_last_successful_github_call_time(cb.message.from_user.id, session)
    if answer:
        await cb.message.answer(f"Последнее успешное обращение к GitHub было {answer}", reply_markup=return_to_the_menu())
    else:
        await cb.message.answer("Успешных обращений к GitHub не было", reply_markup=return_to_the_menu())
    await cb.answer()

#Команда свода ошибок
@admin_router.callback_query(F.data == "get_last_failed_github_call_info")
async def process_get_last_failed_github_call_info(cb: CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as session:
        answer = await get_last_failed_github_call_info(cb.message.from_user.id, session)
    if answer:
        await cb.message.answer(f"Информация о последнем ошибочном обращении к GitHub: {table_to_text(answer)}", reply_markup=return_to_the_menu())
    else:
        await cb.message.answer("Ошибочных обращений к GitHub не было", reply_markup=return_to_the_menu())
    await cb.answer()