from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from infra.db import AsyncSessionLocal
from infra.telegram.keyboards.common_keyboards import *
from .states import *
from commands.common_commands import *
from infra.git.github_service import login_link_github


common_router = Router()

@common_router.message(Command("start"))
async def start_panel(message: Message):
    """Функция отображения основной панели.
       Отображается через команду /start."""
    async with AsyncSessionLocal() as session:
        await create_user(message.from_user.id, message.from_user.username, session)
    await message.answer("Основная панель:", reply_markup=get_start_menu())


@common_router.callback_query(F.data == "start")
async def start_panel(cb: CallbackQuery):
    """Функция отображения основной панели.
       Отображается через кнопку, которая появляется после выполнения команды."""
    await cb.message.answer("Основная панель:", reply_markup=get_start_menu())
    await cb.answer()

@common_router.callback_query(F.data == "login_link_github")
async def process_login_link_github(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции login_link_github"""
    async with AsyncSessionLocal() as session:
        answer = await login_link_github(cb.from_user.id, session)
        await cb.message.answer(f"Запрашиваемый URL: {answer}", reply_markup=return_to_the_start())
    await cb.answer()

@common_router.callback_query(F.data == "logout_user")
async def process_logout_user(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции logout_user"""
    async with AsyncSessionLocal() as session:
        await login_link_github(cb.from_user.id, session)
        await cb.message.answer(f"Аккаунт разлогинен.", reply_markup=return_to_the_start())
    await cb.answer()

@common_router.callback_query(F.data == "set_active_role")
async def process_set_active_role_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции set_active_role"""
    """Установить активную роль пользователя: 'student', 'teacher', 'assistant', 'admin'. С проверкой на доступность роли"""
    await cb.message.answer(
        "Выберите одну из возможных ролей:", reply_markup=choose_role()
    )
    await cb.answer()

@common_router.callback_query(F.data == "change_role_student")
async def process_set_active_role_student(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции change_role_student"""
    role = "student"
    try:
        async with AsyncSessionLocal() as session:
            await set_active_role(cb.from_user.id, role, session)
        await cb.message.answer(f"Роль '{role}' установлена.", reply_markup=go_to_student())
    except:
        await cb.message.answer(f"Не получилось установить роль {role}, возможно, название роли введено неправильно или нет прав доступа.", reply_markup=return_to_the_start())
    await cb.answer()

@common_router.callback_query(F.data == "change_role_teacher")
async def process_set_active_role_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции change_role_teacher"""
    role = "teacher"
    try:
        async with AsyncSessionLocal() as session:
            await set_active_role(cb.from_user.id, role, session)
        await cb.message.answer(f"Роль '{role}' установлена.", reply_markup=go_to_teacher())
    except:
        await cb.message.answer(f"Не получилось установить роль {role}, возможно, название роли введено неправильно или нет прав доступа.", reply_markup=return_to_the_start())
    await cb.answer()

@common_router.callback_query(F.data == "change_role_admin")
async def process_set_active_role_admin(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции change_role_admin"""
    role = "admin"
    try:
        async with AsyncSessionLocal() as session:
            await set_active_role(cb.from_user.id, role, session)
        await cb.message.answer(f"Роль '{role}' установлена.", reply_markup=go_to_admin())
    except:
        await cb.message.answer(f"Не получилось установить роль {role}, возможно, название роли введено неправильно или нет прав доступа.", reply_markup=return_to_the_start())
    await cb.answer()

@common_router.callback_query(F.data == "change_role_assistant")
async def process_set_active_role_assistant(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции change_role_assistant"""
    role = "assistant"
    try:
        async with AsyncSessionLocal() as session:
            await set_active_role(cb.from_user.id, role, session)
        await cb.message.answer(f"Роль '{role}' установлена.", reply_markup=go_to_assistant())
    except:
        await cb.message.answer(f"Не получилось установить роль {role}, возможно, название роли введено неправильно или нет прав доступа.", reply_markup=return_to_the_start())
    await cb.answer()


@common_router.callback_query(F.data == "toggle_global_notifications")
async def process_toggle_global_notifications(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции toggle_global_notifications"""
    async with AsyncSessionLocal() as session:
        await toggle_global_notifications(cb.from_user.id, session)
        await cb.message.answer("Рычаг уведомлений переключен.", reply_markup=return_to_the_start())
    await cb.answer()

@common_router.callback_query(F.data == "change_git_account")
async def process_change_git_account_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции change_git_account"""
    await state.set_state(ChangeGitHubAccount.waiting_login)
    await cb.message.answer(
        "Введи логин гитхаба, на который хочешь переключиться."
    )
    await cb.answer()

@common_router.message(ChangeGitHubAccount.waiting_login)
async def process_change_git_account_second(message: Message, state: FSMContext):
    """Ввод логина для функции change_git_account"""
    login = message.text
    try:
        async with AsyncSessionLocal() as session:
            await change_git_account(message.from_user.id, login, session)
        await message.answer("Аккаунт успешно переключен!", reply_markup=return_to_the_start())
    except:
        await message.answer("Аккаунт не был переключен. Возможно, вы не вошли в этот аккаунт или логин введен неправильно.", reply_markup=return_to_the_start())
    finally:
        await state.clear()

@common_router.callback_query(F.data == "enter_name")
async def process_enter_name_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции enter_name"""
    await state.set_state(EnterName.waiting_name)
    await cb.message.answer(
        "Введите свое ФИО:"
    )
    await cb.answer()

@common_router.message(EnterName.waiting_name)
async def process_enter_name_second(message: Message, state: FSMContext):
    """Ввод имени для функции enter_name"""
    name = message.text
    async with AsyncSessionLocal() as session:
        await enter_name(message.from_user.id, name, session)
    await message.answer("ФИО успешно получено!", reply_markup=return_to_the_start())
    await state.clear()