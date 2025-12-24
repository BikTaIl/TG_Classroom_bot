from pyexpat.errors import messages

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F

from adapters.table_to_text import table_to_text
from infra.db import AsyncSessionLocal
from infra.telegram.keyboards.admin_keyboards import *
from models.db import AccessDenied
from .states import *
from commands.admin_commands import *
from commands.teacher_and_assistant_commands import _get_user_by_username

admin_router = Router()

@admin_router.callback_query(F.data == "start_admin")
async def admin_panel(cb: CallbackQuery):
    """Функция отображения панели администратора
       Отображается только по кнопке, через команду зайти нельзя."""
    await cb.message.edit_text("Панель администратора:", reply_markup=get_admin_menu())
    await cb.answer()

@admin_router.callback_query(F.data == "grant_teacher_role")
async def process_grant_teacher_role_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции grant_teacher_role"""
    await state.set_state(AddTeacher.waiting_organization_name)
    await cb.message.edit_text(
        "Пришли название организации, в которую ты хочешь добавить учителя."
    )
    await cb.answer()

@admin_router.message(AddTeacher.waiting_organization_name)
async def process_grant_teacher_role_second(message: Message, state: FSMContext):
    organisation_name = message.text
    all_data = await state.get_data()
    all_data.update(organisation_name=organisation_name)
    await state.clear()
    await state.set_state(AddTeacher.waiting_username)
    await message.answer(
        "Пришли tg username учителя в формате @username (или просто username)."
    )

@admin_router.message(AddTeacher.waiting_username)
async def process_grant_teacher_role_third(message: Message, state: FSMContext):
    """Ввод имени для функции grant_teacher_role"""
    username = message.text
    all_data = await state.get_data()
    organisation_name = all_data.get("organisation_name")
    try:
        async with AsyncSessionLocal() as session:
            await grant_teacher_role(message.from_user.id, username, session)
            user_id = await _get_user_by_username(username, session)
            await add_organisation(message.from_user.id, user_id, organisation_name, session)
        await message.answer("Учитель добавлен!", reply_markup=return_to_the_menu())
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    finally:
        await state.clear()


@admin_router.callback_query(F.data == "revoke_teacher_role")
async def process_revoke_teacher_role_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции revoke_teacher_role"""
    await state.set_state(RemoveTeacher.waiting_username)
    await cb.message.edit_text(
        "Пришли tg username учителя в формате @username (или просто username)."
    )
    await cb.answer()

@admin_router.message(RemoveTeacher.waiting_username)
async def process_revoke_teacher_role_second(message: Message, state: FSMContext):
    """Ввод имени для функции revoke_teacher_role"""
    username = message.text
    try:
        async with AsyncSessionLocal() as session:
            await revoke_teacher_role(message.from_user.id, username, session)
        await message.answer("Учитель удален!", reply_markup=return_to_the_menu())
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    finally:
        await state.clear()

@admin_router.callback_query(F.data == "ban_user")
async def process_ban_user_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции ban_user"""
    await state.set_state(Ban.waiting_username)
    await cb.message.edit_text(
        "Пришли tg username пользователя в формате @username (или просто username)."
    )
    await cb.answer()

@admin_router.message(Ban.waiting_username)
async def process_ban_user_second(message: Message, state: FSMContext):
    """Ввод имени для функции ban_user"""
    username = message.text
    try:
        async with AsyncSessionLocal() as session:
            await ban_user(message.from_user.id, username, session)
        await message.answer("Пользователь забанен!", reply_markup=return_to_the_menu())
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    finally:
        await state.clear()

@admin_router.callback_query(F.data == "unban_user")
async def process_unban_user_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции unban_user"""
    await state.set_state(Unban.waiting_username)
    await cb.message.edit_text(
        "Пришли tg username пользователя в формате @username (или просто username)."
    )
    await cb.answer()

@admin_router.message(Unban.waiting_username)
async def process_unban_user_second(message: Message, state: FSMContext):
    """Ввод имени для функции unban_user"""
    username = message.text
    try:
        async with AsyncSessionLocal() as session:
            await unban_user(message.from_user.id, username, session)
        await message.answer("Пользователь разбанен!", reply_markup=return_to_the_menu())
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    finally:
        await state.clear()

@admin_router.callback_query(F.data == "get_error_count_for_day")
async def process_get_error_count_for_day_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_error_count_for_day"""
    await state.set_state(FindErrors.waiting_date)
    await cb.message.edit_text(
        "Пришли дату, для которой хочешь узнать сводку в формате ГГГГ-ММ-ДД, или напиши '-' для общей сводки"
    )
    await cb.answer()

@admin_router.message(FindErrors.waiting_date)
async def process_get_error_count_for_day_second(message: Message, state: FSMContext):
    """Ввод даты для функции get_error_count_for_day"""
    target_date: list[str] = message.text.split('-')
    try:
        async with AsyncSessionLocal() as session:
            try:
                result = await get_error_count_for_day(message.from_user.id, date(day=int(target_date[2]), month=int(target_date[1]), year=int(target_date[0])), session)
            except TypeError:
                result = await get_error_count_for_day(message.from_user.id, session)
        await message.answer(f"Ошибок за указанный период: {result}", reply_markup=return_to_the_menu())
        await state.clear()
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    finally:
        await state.clear()

@admin_router.callback_query(F.data == "get_last_successful_github_call_time")
async def process_get_last_successful_github_call_time(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_last_successful_github_call_time"""
    try:
        async with AsyncSessionLocal() as session:
            answer = await get_last_successful_github_call_time(cb.from_user.id, session)
        if answer:
            await cb.message.edit_text(f"Последнее успешное обращение к GitHub было {answer}", reply_markup=return_to_the_menu())
        else:
            await cb.message.edit_text("Успешных обращений к GitHub не было", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@admin_router.callback_query(F.data == "get_last_failed_github_call_info")
async def process_get_last_failed_github_call_info(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_last_failed_github_call_info"""
    try:
        async with AsyncSessionLocal() as session:
            answer = await get_last_failed_github_call_info(cb.from_user.id, session)
        if answer:
            await cb.message.edit_text(f"Информация о последнем ошибочном обращении к GitHub: {table_to_text(answer)}", reply_markup=return_to_the_menu())
        else:
            await cb.message.edit_text("Ошибочных обращений к GitHub не было", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@admin_router.callback_query(F.data == "delete_organization")
async def process_delete_organization_first(cb: CallbackQuery, state: FSMContext):
    await state.set_state(DeleteOrganisation.waiting_name)
    await cb.message.edit_text(
        "Введите название организации, которую хотите удалить:"
    )
    await cb.answer()

@admin_router.message(DeleteOrganisation.waiting_name)
async def process_delete_organization_first(message: Message, state: FSMContext):
    name = message.text
    try:
        async with AsyncSessionLocal() as session:
            await delete_organization(message.from_user.id, name, session)
        await message.answer("Организация успешно удалена", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    finally:
        await state.clear()