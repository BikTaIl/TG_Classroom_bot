from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from infra.db import AsyncSessionLocal
from infra.telegram.keyboards.teacher_keyboards import *
from .states import *
from commands.sync import sync_function
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
    await cb.message.update_text("Выберите сводку:", reply_markup=summaries())
    await cb.answer()

@teacher_router.callback_query(F.data == "set_teacher_active_course_teacher")
async def process_set_teacher_active_course_teacher_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции set_teacher_active_course_teacher"""
    await state.set_state(ChangeCourseTeacher.waiting_course_name)
    await cb.message.update_text(
        "Введите название желаемого курса или '-', если хотите сбросить курс"
    )
    await cb.answer()

@teacher_router.message(ChangeCourseTeacher.waiting_course_name)
async def process_set_teacher_active_course_teacher_second(message: Message, state: FSMContext):
    """Ввод ID курса для функции set_teacher_active_course_teacher"""
    course_name = message.text
    try:
        if course_name == '-':
            await state.update_data(course_name=None)
            await message.answer("Курс сброшен", reply_markup=return_to_the_menu())
        else:
            await state.update_data(course_name=int(course_name))
            await message.answer("Курс установлен", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())

@teacher_router.callback_query(F.data == "set_teacher_active_assignment_teacher")
async def process_set_teacher_active_assignment_teacher_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции set_teacher_active_assignment_teacher"""
    await state.set_state(ChangeAssignmentTeacher.waiting_assignment_name)
    await cb.message.update_text(
        "Введите название желаемого задания или '-', если хотите сбросить его."
    )
    await cb.answer()

@teacher_router.message(ChangeAssignmentTeacher.waiting_assignment_name)
async def process_set_teacher_active_assignment_teacher_second(message: Message, state: FSMContext):
    """Ввод ID курса для функции set_teacher_active_assignment_teacher"""
    assignment_name = message.text
    all_data = await state.get_data()
    course_name = all_data.get("course_name")
    try:
        if assignment_name == '-':
            await state.update_data(assignment_name=None)
            await message.answer("Задание сброшено", reply_markup=return_to_the_menu())
        elif not course_name:
            await message.answer("Для выбора задания выберите курс.", reply_markup=choose_course())
        else:
            await state.update_data(assignment_name=int(assignment_name))
            await message.answer("Задание установлено", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())


@teacher_router.callback_query(F.data == "get_course_students_overview_teacher")
async def process_get_course_students_overview_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_course_students_overview_teacher"""
    all_data = await state.get_data()
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            course_id = await find_course(cb.from_user.id, course_name, session)
            overview = await get_course_students_overview(cb.from_user.id, course_id, session)
            print(overview)
        await cb.message.update_text(await table_to_text(overview), reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@teacher_router.callback_query(F.data == "get_assignment_students_status_teacher")
async def process_get_assignment_students_status_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_assignment_students_status_teacher"""
    all_data = await state.get_data()
    assignment_name = all_data.get("assignment_name")
    course_name = all_data.get("course_name")
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


@teacher_router.callback_query(F.data == "get_classroom_users_without_bot_accounts_teacher")
async def process_get_classroom_users_without_bot_accounts_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_classroom_users_without_bot_accounts_teacher"""
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


@teacher_router.callback_query(F.data == "get_course_deadlines_overview_teacher")
async def process_get_course_deadlines_overview_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_course_deadlines_overview_teacher"""
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


@teacher_router.callback_query(F.data == "get_tasks_to_grade_summary_teacher")
async def process_get_tasks_to_grade_summary_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_tasks_to_grade_summary_teacher"""
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


@teacher_router.callback_query(F.data == "get_manual_check_submissions_summary_teacher")
async def process_get_manual_check_submissions_summary_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_manual_check_submissions_summary_teacher"""
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


@teacher_router.callback_query(F.data == "get_teacher_deadline_notification_payload_teacher")
async def process_get_teacher_deadline_notification_payload_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_teacher_deadline_notification_payload_teacher"""
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
            await cb.message.update_text("Данных нет", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@teacher_router.callback_query(F.data == "add_course_assistant_teacher")
async def process_add_course_assistant_teacher_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции add_course_assistant_teacher"""
    await state.set_state(AddAssistant.waiting_username)
    await cb.message.update_text(
        "Введите ник ассистента в виде @username или username:"
    )
    await cb.answer()

@teacher_router.message(AddAssistant.waiting_username)
async def process_add_course_assistant_teacher_second(message: Message, state: FSMContext):
    """Ввод имени для функции add_course_assistant_teacher"""
    username = message.text
    all_data = await state.get_data()
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            course_id = await find_course(message.from_user.id, course_name, session)
            await add_course_assistant(message.from_user.id, course_id, username, session)
        await message.answer("Ассистент успешно добавлен!", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())


@teacher_router.callback_query(F.data == "remove_course_assistant_teacher")
async def process_remove_course_assistant_teacher_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции remove_course_assistant_teacher"""
    await state.set_state(RemoveAssistant.waiting_username)
    await cb.message.update_text(
        "Введите ник ассистента в виде @username или username:"
    )
    await cb.answer()

@teacher_router.message(RemoveAssistant.waiting_username)
async def process_remove_course_assistant_teacher_second(message: Message, state: FSMContext):
    """Ввод имени для функции remove_course_assistant_teacher"""
    username = message.text
    all_data = await state.get_data()
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            course_id = await find_course(message.from_user.id, course_name, session)
            await remove_course_assistant(message.from_user.id, course_id, username, session)
        await message.answer("Ассистент успешно удален!", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())


@teacher_router.callback_query(F.data == "create_course_announcement_teacher")
async def process_create_course_announcement_teacher_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции create_course_announcement_teacher"""
    await state.set_state(AddAnnouncement.waiting_text)
    await cb.message.update_text(
        "Введите ник ассистента в виде @username или username:"
    )
    await cb.answer()

@teacher_router.message(AddAnnouncement.waiting_text)
async def process_create_course_announcement_teacher_second(message: Message, state: FSMContext):
    """Ввод имени для функции create_course_announcement_teacher"""
    text = message.text
    all_data = await state.get_data()
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            course_id = await find_course(message.from_user.id, course_name, session)
            students_id = await create_course_announcement(message.from_user.id, course_name, text, session)
        for student_id in students_id:
            await message.bot.send_message(student_id, text)
        await message.answer("Уведомление успешно создано!", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())

@teacher_router.callback_query(F.data == "trigger_manual_sync_for_teacher_teacher")
async def process_get_course_deadlines_overview_teacher(cb: CallbackQuery):
    """Запуск по кнопке функции trigger_manual_sync_for_teacher_teacher"""
    try:
        async with AsyncSessionLocal() as session:
            done = await trigger_manual_sync_for_teacher(cb.from_user.id, session)
            async with AsyncSessionLocal() as sync_session:
                await sync_function(sync_session)
        if done:
            await cb.message.update_text("Сессия синхронизирована")
        else:
            await cb.message.update_text("Сессия была обновлена уже 3 раза за сутки. Нет доступа.")
    except AccessDenied as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()