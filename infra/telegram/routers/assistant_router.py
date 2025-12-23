from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram import Router, F
from infra.db import AsyncSessionLocal
from infra.telegram.keyboards.assistant_keyboards import *
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
async def assistant_summary_panel(cb: CallbackQuery):
    await cb.message.edit_text("Выберите сводку:", reply_markup=summaries())
    await cb.answer()

@assistant_router.callback_query(F.data == "choose_assistant_active_course")
async def process_choose_assistant_active_course(cb: CallbackQuery, state: FSMContext):
    try:
        async with AsyncSessionLocal() as session:
            courses = await find_assistants_courses(cb.from_user.id, session)
        await cb.message.edit_text("Выберите курс или сбросьте его:", reply_markup=choose_course(courses, 0))
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@assistant_router.callback_query(F.data.startswith("set_assistant_active_course"))
async def process_set_assistant_active_course(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split(":")
    course_id = int(data[0])
    try:
        if course_id == 'Сбросить курс':
            await state.update_data(course_id=None)
            await cb.message.answer("Курс сброшен", reply_markup=return_to_the_menu())
        else:
            await state.update_data(course_id=course_id)
            await cb.message.answer("Курс установлен", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@assistant_router.callback_query(F.data.startswith("previous_paper_course_assistant"))
async def process_previous_page(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split(":")
    page = int(data[1])
    try:
        async with AsyncSessionLocal() as session:
            courses = await find_assistants_courses(cb.from_user.id, session)
        await cb.message.edit_text("Выберите курс:", reply_markup=choose_course(courses, page - 1))
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@assistant_router.callback_query(F.data.startswith("next_paper_course_assistant"))
async def process_next_page(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split(":")
    page = int(data[1])
    try:
        async with AsyncSessionLocal() as session:
            courses = await find_assistants_courses(cb.from_user.id, session)
        await cb.message.edit_text("Выберите курс:", reply_markup=choose_course(courses, page + 1))
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@assistant_router.callback_query(F.data == "choose_assistant_active_assignment")
async def process_choose_assistant_active_assignment(cb: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        if course_id:
            async with AsyncSessionLocal() as session:
                assignments = await find_assignments_by_course_id(course_id, session)
            await cb.message.edit_text("Выберите задание или сбростье его:", reply_markup=choose_assignment(assignments, 0))
        else:
            await cb.message.edit_text("Чтобы выбрать активное задание, нужно выбрать активный курс.", reply_markup=have_to_choose_course())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@assistant_router.callback_query(F.data.startswith("set_assistant_active_assignment"))
async def process_set_assistant_active_assignment(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split(":")
    assignment_id = int(data[1])
    try:
        async with AsyncSessionLocal() as session:
            if assignment_id == 'Сбросить задание':
                await state.update_data(assignment_id=None)
                await cb.message.answer("Задание сброшено", reply_markup=return_to_the_menu())
            else:
                await state.update_data(assignment_id=assignment_id)
                await cb.message.answer("Задание установлено", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@assistant_router.callback_query(F.data.startswith("previous_paper_assignment_assistant"))
async def process_previous_page(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split(":")
    page = int(data[1])
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        async with AsyncSessionLocal() as session:
            assignments = await find_assignments_by_course_id(course_id, session)
        await cb.message.edit_text("Выберите задание:", reply_markup=choose_assignment(assignments, page - 1))
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@assistant_router.callback_query(F.data.startswith("next_paper_assignment_assistant"))
async def process_next_page(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split(":")
    page = int(data[1])
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        async with AsyncSessionLocal() as session:
            assignments = await find_assignments_by_course_id(course_id, session)
        await cb.message.edit_text("Выберите задание:", reply_markup=choose_assignment(assignments, page + 1))
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@assistant_router.callback_query(F.data == "get_course_students_overview_assistant")
async def process_get_course_students_overview_assistant(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_course_students_overview_assistant"""
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        async with AsyncSessionLocal() as session:
            overview = await get_course_students_overview(cb.from_user.id, course_id, session)
        await cb.message.edit_text(await table_to_text(overview), reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@assistant_router.callback_query(F.data == "get_assignment_students_status_assistant")
async def process_get_assignment_students_status_assistant(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_assignment_students_status_assistant"""
    all_data = await state.get_data()
    assignment_id = all_data.get("assignment_id")
    course_id = all_data.get("couse_id")
    try:
        async with AsyncSessionLocal() as session:
            overview = await get_assignment_students_status(cb.from_user.id, assignment_id, session)
        await cb.message.edit_text(await table_to_text(overview), reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()


@assistant_router.callback_query(F.data == "get_classroom_users_without_bot_accounts_assistant")
async def process_get_classroom_users_without_bot_accounts_assistant(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_classroom_users_without_bot_accounts_assistant"""
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        async with AsyncSessionLocal() as session:
            overview = await get_classroom_users_without_bot_accounts(cb.from_user.id, course_id, session)
        result = ""
        for username in overview:
            result += username + "\n"
        await cb.message.edit_text(result, reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()


@assistant_router.callback_query(F.data == "get_course_deadlines_overview_assistant")
async def process_get_course_deadlines_overview_assistant(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_course_deadlines_overview_assistant"""
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        async with AsyncSessionLocal() as session:
            overview = await get_course_deadlines_overview(cb.from_user.id, course_id, session)
        await cb.message.edit_text(await table_to_text(overview), reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()


@assistant_router.callback_query(F.data == "get_tasks_to_grade_summary_assistant")
async def process_get_tasks_to_grade_summary_assistant(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_tasks_to_grade_summary_assistant"""
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        async with AsyncSessionLocal() as session:
            overview = await get_tasks_to_grade_summary(cb.from_user.id, course_id, session)
        await cb.message.edit_text(await table_to_text(overview), reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()


@assistant_router.callback_query(F.data == "get_manual_check_submissions_summary_assistant")
async def process_get_manual_check_submissions_summary_assistant(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_manual_check_submissions_summary_assistant"""
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        async with AsyncSessionLocal() as session:
            overview = await get_manual_check_submissions_summary(cb.from_user.id, course_id, session)
        await cb.message.edit_text(await table_to_text(overview), reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()


@assistant_router.callback_query(F.data == "get_assistant_deadline_notification_payload_assistant")
async def process_get_assistant_deadline_notification_payload_assistant(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_assistant_deadline_notification_payload_assistant"""
    all_data = await state.get_data()
    assignment_id = all_data.get("assignment_id")
    course_id = all_data.get("course_id")
    try:
        async with AsyncSessionLocal() as session:
            overview = await get_assignment_students_status(cb.from_user.id, assignment_id, session)
        if overview:
            await cb.message.edit_text(await table_to_text(overview), reply_markup=return_to_the_menu())
        else:
            await cb.message.edit_text("Данных нет")
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@assistant_router.callback_query(F.data == "select_manual_check_assignment_assistant")
async def process_select_manual_check_assignment_assistant(cb: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    assignment_id = all_data.get("assignment_id")
    try:
        async with AsyncSessionLocal() as session:
            await select_manual_check_assignment(assignment_id, session)
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()