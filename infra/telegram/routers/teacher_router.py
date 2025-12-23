from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from infra.db import AsyncSessionLocal
from infra.telegram.keyboards.teacher_keyboards import *
from .states import *
from commands.teacher_and_assistant_commands import *
from adapters.table_to_text import table_to_text

teacher_router = Router()

@teacher_router.callback_query(F.data == "start_teacher")
async def teacher_panel(cb: CallbackQuery):
    """Функция отображения панели учителя.
       Отображается только по кнопке, через команду зайти нельзя."""
    await cb.message.answer("Панель учителя:", reply_markup=get_teacher_menu())
    await cb.answer()

@teacher_router.callback_query(F.data == "get_summary_teacher")
async def teacher_summary_panel(cb: CallbackQuery):
    await cb.message.edit_text("Выберите сводку:", reply_markup=summaries())
    await cb.answer()

@teacher_router.callback_query(F.data == "choose_teacher_active_course")
async def process_choose_teacher_active_course(cb: CallbackQuery, state: FSMContext):
    try:
        async with AsyncSessionLocal() as session:
            courses = await find_teachers_courses(cb.from_user.id, session)
        await cb.message.edit_text("Выберите курс или сбростье его:", reply_markup=choose_course(courses, 0))
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@teacher_router.callback_query(F.data.startswith("set_teacher_active_course"))
async def process_set_teacher_active_course(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split(":")
    course_id = int(data[1])
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

@teacher_router.callback_query(F.data.startswith("previous_paper_course_teacher"))
async def process_previous_page(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split(":")
    page = int(data[1])
    try:
        async with AsyncSessionLocal() as session:
            courses = await find_teachers_courses(cb.from_user.id, session)
        await cb.message.edit_text("Выберите курс:", reply_markup=choose_course(courses, page - 1))
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@teacher_router.callback_query(F.data.startswith("next_paper_course_teacher"))
async def process_next_page(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split(":")
    page = int(data[1])
    try:
        async with AsyncSessionLocal() as session:
            courses = await find_teachers_courses(cb.from_user.id, session)
        await cb.message.edit_text("Выберите курс:", reply_markup=choose_course(courses, page + 1))
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@teacher_router.callback_query(F.data == "choose_teacher_active_assignment")
async def process_choose_teacher_active_assignment(cb: CallbackQuery, state: FSMContext):
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

@teacher_router.callback_query(F.data.startswith("set_teacher_active_assignment"))
async def process_set_teacher_active_assignment(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split(":")
    assignment_id = int(data[1])
    try:
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

@teacher_router.callback_query(F.data.startswith("previous_paper_assignment_teacher"))
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

@teacher_router.callback_query(F.data.startswith("next_paper_assignment_teacher"))
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

@teacher_router.callback_query(F.data == "get_course_students_overview_teacher")
async def process_get_course_students_overview_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_course_students_overview_teacher"""
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        async with AsyncSessionLocal() as session:
            overview = await get_course_students_overview(cb.from_user.id, course_id, session)
        await cb.message.answer(await table_to_text(overview), reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@teacher_router.callback_query(F.data == "get_assignment_students_status_teacher")
async def process_get_assignment_students_status_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_assignment_students_status_teacher"""
    all_data = await state.get_data()
    assignment_id = all_data.get("assignment_id")
    course_id = all_data.get("course_id")
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


@teacher_router.callback_query(F.data == "get_classroom_users_without_bot_accounts_teacher")
async def process_get_classroom_users_without_bot_accounts_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_classroom_users_without_bot_accounts_teacher"""
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


@teacher_router.callback_query(F.data == "get_course_deadlines_overview_teacher")
async def process_get_course_deadlines_overview_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_course_deadlines_overview_teacher"""
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


@teacher_router.callback_query(F.data == "get_tasks_to_grade_summary_teacher")
async def process_get_tasks_to_grade_summary_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_tasks_to_grade_summary_teacher"""
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


@teacher_router.callback_query(F.data == "get_manual_check_submissions_summary_teacher")
async def process_get_manual_check_submissions_summary_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_manual_check_submissions_summary_teacher"""
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


@teacher_router.callback_query(F.data == "get_teacher_deadline_notification_payload_teacher")
async def process_get_teacher_deadline_notification_payload_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_teacher_deadline_notification_payload_teacher"""
    all_data = await state.get_data()
    assignment_id = all_data.get("assignment_id")
    course_id = all_data.get("course_id")
    try:
        async with AsyncSessionLocal() as session:
            overview = await get_assignment_students_status(cb.from_user.id, assignment_id, session)
        if overview:
            await cb.message.edit_text(await table_to_text(overview), reply_markup=return_to_the_menu())
        else:
            await cb.message.edit_text("Данных нет", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@teacher_router.callback_query(F.data == "add_course_assistant_teacher")
async def process_add_course_assistant_teacher_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции add_course_assistant_teacher"""
    await state.set_state(AddAssistant.waiting_username)
    await cb.message.edit_text(
        "Введите ник ассистента в виде @username или username:"
    )
    await cb.answer()

@teacher_router.message(AddAssistant.waiting_username)
async def process_add_course_assistant_teacher_second(message: Message, state: FSMContext):
    """Ввод имени для функции add_course_assistant_teacher"""
    username = message.text
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        async with AsyncSessionLocal() as session:
            await add_course_assistant(message.from_user.id, course_id, username, session)
        await message.answer("Ассистент успешно добавлен!", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    finally:
        await state.clear()


@teacher_router.callback_query(F.data == "remove_course_assistant_teacher")
async def process_remove_course_assistant_teacher_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции remove_course_assistant_teacher"""
    await state.set_state(RemoveAssistant.waiting_username)
    await cb.message.edit_text(
        "Введите ник ассистента в виде @username или username:"
    )
    await cb.answer()

@teacher_router.message(RemoveAssistant.waiting_username)
async def process_remove_course_assistant_teacher_second(message: Message, state: FSMContext):
    """Ввод имени для функции remove_course_assistant_teacher"""
    username = message.text
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        async with AsyncSessionLocal() as session:
            await remove_course_assistant(message.from_user.id, course_id, username, session)
        await message.answer("Ассистент успешно удален!", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    finally:
        await state.clear()


@teacher_router.callback_query(F.data == "create_course_announcement_teacher")
async def process_create_course_announcement_teacher_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции create_course_announcement_teacher"""
    await state.set_state(AddAnnouncement.waiting_text)
    await cb.message.edit_text(
        "Введите ник ассистента в виде @username или username:"
    )
    await cb.answer()

@teacher_router.message(AddAnnouncement.waiting_text)
async def process_create_course_announcement_teacher_second(message: Message, state: FSMContext):
    """Ввод имени для функции create_course_announcement_teacher"""
    text = message.text
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        async with AsyncSessionLocal() as session:
            students_id = await create_course_announcement(message.from_user.id, course_id, session)
        for student_id in students_id:
            await message.bot.send_message(student_id, text)
        await message.answer("Уведомление успешно создано!", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    finally:
        await state.clear()

@teacher_router.callback_query(F.data == "trigger_manual_sync_for_teacher_teacher")
async def process_get_course_deadlines_overview_teacher(cb: CallbackQuery):
    """Запуск по кнопке функции trigger_manual_sync_for_teacher_teacher"""
    try:
        async with AsyncSessionLocal() as session:
            done = await trigger_manual_sync_for_teacher(cb.from_user.id, session)
            async with AsyncSessionLocal() as sync_session:
                await sync_function(sync_session)
        if done:
            await cb.message.edit_text("Сессия синхронизирована")
        else:
            await cb.message.edit_text("Сессия была обновлена уже 3 раза за сутки. Нет доступа.")
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@teacher_router.callback_query(F.data == "select_manual_check_assignment_teacher")
async def process_select_manual_check_assignment_teacher(cb: CallbackQuery, state: FSMContext):
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