from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from infra.db import AsyncSessionLocal
from infra.telegram.keyboards.assistant_keyboards import *
from .states import *
from commands.teacher_and_assistant_commands import *
from adapters.table_to_text import table_to_text

assistant_router = Router()

@assistant_router.callback_query(F.data == "start_assistant")
async def admin_panel(cb: CallbackQuery):
    """Функция отображения панели ассистента.
       Отображается только по кнопке, через команду зайти нельзя."""
    await cb.message.answer("Панель ассистента:", reply_markup=get_assistant_menu())
    await cb.answer()

@assistant_router.callback_query(F.data == "get_summary_assistant")
async def teacher_summary_panel(cb: CallbackQuery):
    await cb.message.update_text("Выберите сводку:", reply_markup=summaries())
    await cb.answer()

@assistant_router.callback_query(F.data == "set_teacher_active_course_assistant")
async def process_set_teacher_active_course_assistant_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции set_teacher_active_course_assistant"""
    await state.set_state(ChangeCourseAssistant.waiting_course_name)
    await cb.message.update_text(
        "Введите название желаемого курса или '-', если хотите сбросить курс"
    )
    await cb.answer()

@assistant_router.message(ChangeCourseAssistant.waiting_course_name)
async def process_set_teacher_active_course_assistant_second(message: Message, state: FSMContext):
    """Ввод ID курса для функции set_teacher_active_course_assistant"""
    course_name = message.text
    try:
        async with AsyncSessionLocal() as session:
            if course_name == '-':
                await state.update_data(course_name=None)
                await message.answer("Курс сброшен", reply_markup=return_to_the_menu())
            else:
                await state.update_data(course_name=course_name)
                await message.answer("Курс установлен", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())


@assistant_router.callback_query(F.data == "set_teacher_active_assignment_assistant")
async def process_set_teacher_active_assignment_assistant_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции set_teacher_active_assignment_assistant"""
    await state.set_state(ChangeAssignmentAssistant.waiting_assignment_name)
    await cb.message.update_text(
        "Введите название желаемого задания или '-', если хотите сбросить его."
    )
    await cb.answer()

@assistant_router.message(ChangeAssignmentAssistant.waiting_assignment_name)
async def process_set_teacher_active_assignment_assistant_second(message: Message, state: FSMContext):
    """Ввод ID курса для функции set_teacher_active_assignment_assistant"""
    assignment_name = message.text
    all_data = await state.get_data()
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            if assignment_name == '-':
                await state.update_data(assignment_name=None)
                await message.answer("Задание сброшено", reply_markup=return_to_the_menu())
            elif not course_name:
                await message.answer("Для выбора задания выберите курс.", reply_markup=choose_course())
            else:
                await state.update_data(assignment_name=assignment_name)
                await message.answer("Задание установлено", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())


@assistant_router.callback_query(F.data == "get_course_students_overview_assistant")
async def process_get_course_students_overview_assistant(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_course_students_overview_assistant"""
    all_data = await state.get_data()
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            course_id = await find_course(cb.from_user.id, course_name, session)
            overview = await get_course_students_overview(cb.from_user.id, course_id, session)
        await cb.message.update_text(await table_to_text(overview), reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@assistant_router.callback_query(F.data == "get_assignment_students_status_assistant")
async def process_get_assignment_students_status_assistant(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_assignment_students_status_assistant"""
    all_data = await state.get_data()
    assignment_name = all_data.get("assignment_name")
    course_name = all_data.get("couse_name")
    try:
        async with AsyncSessionLocal() as session:
            assignment_id = await find_assignment(str(await find_course(cb.from_user.id, course_name, session)), assignment_name, session)
            overview = await get_assignment_students_status(cb.from_user.id, assignment_id, session)
        await cb.message.update_text(await table_to_text(overview), reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()


@assistant_router.callback_query(F.data == "get_classroom_users_without_bot_accounts_assistant")
async def process_get_classroom_users_without_bot_accounts_assistant(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_classroom_users_without_bot_accounts_assistant"""
    all_data = await state.get_data()
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            course_id = await find_course(cb.from_user.id, course_name, session)
            overview = await get_classroom_users_without_bot_accounts(cb.from_user.id, course_id, session)
        result = ""
        for username in overview:
            result += username + "\n"
        await cb.message.update_text(result, reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()


@assistant_router.callback_query(F.data == "get_course_deadlines_overview_assistant")
async def process_get_course_deadlines_overview_assistant(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_course_deadlines_overview_assistant"""
    all_data = await state.get_data()
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            course_id = await find_course(cb.from_user.id, course_name, session)
            overview = await get_course_deadlines_overview(cb.from_user.id, course_id, session)
        await cb.message.update_text(await table_to_text(overview), reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()


@assistant_router.callback_query(F.data == "get_tasks_to_grade_summary_assistant")
async def process_get_tasks_to_grade_summary_assistant(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_tasks_to_grade_summary_assistant"""
    all_data = await state.get_data()
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            course_id = await find_course(cb.from_user.id, course_name, session)
            overview = await get_tasks_to_grade_summary(cb.from_user.id, course_id, session)
        await cb.message.update_text(await table_to_text(overview), reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()


@assistant_router.callback_query(F.data == "get_manual_check_submissions_summary_assistant")
async def process_get_manual_check_submissions_summary_assistant(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_manual_check_submissions_summary_assistant"""
    all_data = await state.get_data()
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            course_id = await find_course(cb.from_user.id, course_name, session)
            overview = await get_manual_check_submissions_summary(cb.from_user.id, course_id, session)
        await cb.message.update_text(await table_to_text(overview), reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()


@assistant_router.callback_query(F.data == "get_teacher_deadline_notification_payload_assistant")
async def process_get_teacher_deadline_notification_payload_assistant(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_teacher_deadline_notification_payload_assistant"""
    all_data = await state.get_data()
    assignment_name = all_data.get("assignment_name")
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            assignment_id = await find_assignment(str(await find_course(cb.from_user.id, course_name, session)), assignment_name, session)
            overview = await get_assignment_students_status(cb.from_user.id, assignment_id, session)
        if overview:
            await cb.message.update_text(await table_to_text(overview), reply_markup=return_to_the_menu())
        else:
            await cb.message.update_text("Данных нет")
    except AccessDenied as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()