import asyncio
from pyexpat.errors import messages

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from infra.db import AsyncSessionLocal
from infra.telegram.keyboards.common_keyboards import *
from .states import *
from commands.common_commands import *


common_router = Router()

@common_router.message(Command("start"))
async def start_panel(message: Message):
    """Отображение клавиатуры"""
    await message.answer("Основная панель:", reply_markup=get_start_menu())


@common_router.callback_query(F.data == "start")
async def start_panel(cb: CallbackQuery):
    await cb.message.answer("Основная панель:", reply_markup=get_start_menu())

@common_router.callback_query(F.data == "login_link_github")
async def process_login_link_github(cb: CallbackQuery, state: FSMContext):
    """Вернуть URL для привязки GitHub-аккаунта к пользователю Telegram."""
    async with AsyncSessionLocal() as session:
        answer = await login_link_github(cb.message.from_user.id, session)
        await cb.message.answer(f"Запрашиваемый URL: {answer}", reply_markup=return_to_the_start())

@common_router.callback_query(F.data == "logout_user")
async def process_logout_user(cb: CallbackQuery, state: FSMContext):
    """Разлогинить текущий акк из GitHub."""
    async with AsyncSessionLocal() as session:
        await login_link_github(cb.message.from_user.id, session)
        await cb.message.answer(f"Аккаунт разлогинен.", reply_markup=return_to_the_start())

@common_router.callback_query(F.data == "set_active_role")
async def process_set_active_role_first(cb: CallbackQuery, state: FSMContext):
    """Установить активную роль пользователя: 'student', 'teacher', 'assistant', 'admin'. С проверкой на доступность роли"""
    await cb.message.answer(
        "Выберите одну из возможных ролей:", reply_markup=choose_role()
    )
    await cb.answer()

@common_router.callback_query(F.data == "change_role_student")
async def process_set_active_role_student(cb: CallbackQuery, state: FSMContext):
    role = "student"
    try:
        async with AsyncSessionLocal() as session:
            await set_active_role(cb.message.from_user.id, role, session)
        await cb.message.answer(f"Роль '{role}' установлена.", reply_markup=return_to_the_start())
    except:
        await cb.message.answer(f"Не получилось установить роль {role}, возможно, название роли введено неправильно или нет прав доступа.", reply_markup=return_to_the_start())

@common_router.callback_query(F.data == "change_role_teacher")
async def process_set_active_role_teacher(cb: CallbackQuery, state: FSMContext):
    role = "teacher"
    try:
        async with AsyncSessionLocal() as session:
            await set_active_role(cb.message.from_user.id, role, session)
        await cb.message.answer(f"Роль '{role}' установлена.", reply_markup=return_to_the_start())
    except:
        await cb.message.answer(f"Не получилось установить роль {role}, возможно, название роли введено неправильно или нет прав доступа.", reply_markup=return_to_the_start())

@common_router.callback_query(F.data == "change_role_admin")
async def process_set_active_role_admin(cb: CallbackQuery, state: FSMContext):
    role = "admin"
    try:
        async with AsyncSessionLocal() as session:
            await set_active_role(cb.message.from_user.id, role, session)
        await cb.message.answer(f"Роль '{role}' установлена.", reply_markup=go_to_admin())
    except:
        await cb.message.answer(f"Не получилось установить роль {role}, возможно, название роли введено неправильно или нет прав доступа.", reply_markup=return_to_the_start())

@common_router.callback_query(F.data == "change_role_assistant")
async def process_set_active_role_assistant(cb: CallbackQuery, state: FSMContext):
    role = "assistant"
    try:
        async with AsyncSessionLocal() as session:
            await set_active_role(cb.message.from_user.id, role, session)
        await cb.message.answer(f"Роль '{role}' установлена.", reply_markup=return_to_the_start())
    except:
        await cb.message.answer(f"Не получилось установить роль {role}, возможно, название роли введено неправильно или нет прав доступа.", reply_markup=return_to_the_start())


@common_router.callback_query(F.data == "toggle_global_notifications")
async def process_toggle_global_notifications(cb: CallbackQuery, state: FSMContext):
    """Глобально сменить рычажок уведомлений по дд для пользователя."""
    async with AsyncSessionLocal() as session:
        await toggle_global_notifications(cb.message.from_user.id, session)
        await cb.message.answer("Рычаг уведомлений переключен.", reply_markup=return_to_the_start())

@common_router.callback_query(F.data == "change_git_account")
async def process_change_git_account_first(cb: CallbackQuery, state: FSMContext):
    """Сменить гитхаб-аккаунт на другой залогиненный"""
    await state.set_state(ChangeGitHubAccount.waiting_login)
    await cb.message.answer(
        "Введи логин гитхаба, на который хочешь переключиться."
    )
    await cb.answer()

@common_router.message(ChangeGitHubAccount.waiting_login)
async def process_change_git_account_second(message: Message, state: FSMContext):
    login = message.text
    try:
        async with AsyncSessionLocal() as session:
            await change_git_account(message.from_user.id, login, session)
        await message.answer("Аккаунт успешно переключен!", reply_markup=return_to_the_start())
    except:
        await message.answer("Аккаунт не был переключен. Возможно, вы не вошли в этот аккаунт или логин введен неправильно.", reply_markup=return_to_the_start())
    finally:
        await state.clear()
