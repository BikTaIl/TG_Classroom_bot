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
async def admin_panel(cb: CallbackQuery):
    """Функция отображения панели учителя.
       Отображается только по кнопке, через команду зайти нельзя."""
    await cb.message.answer("Панель учителя:", reply_markup=get_teacher_menu())
    await cb.answer()

@teacher_router.callback_query(F.data == "set_teacher_active_course_teacher")
async def process_set_teacher_active_course_teacher_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции set_teacher_active_course_teacher"""
    await state.set_state(ChangeCourse.waiting_course_id)
    await cb.message.answer(
        "Введите ID желаемого курса или '-', если хотите сбросить курс"
    )
    await cb.answer()

@teacher_router.message(ChangeCourse.waiting_course_id)
async def process_set_teacher_active_course_teacher_second(message: Message, state: FSMContext):
    """Ввод ID курса для функции set_teacher_active_course_teacher"""
    course_id = message.text
    try:
        async with AsyncSessionLocal() as session:
            if course_id == '-':
                await state.update_data(course_id=None)
                await message.answer("Курс сброшен", reply_markup=return_to_the_menu())
            else:
                await state.update_data(course_id=course_id)
                await message.answer("Курс установлен", reply_markup=return_to_the_menu())
    except AccessDenied:
        await message.answer("ID курса написан неправильно или к нему нет доступа", reply_markup=return_to_the_menu())


@teacher_router.callback_query(F.data == "set_teacher_active_assignment_teacher")
async def process_set_teacher_active_assignment_teacher_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции set_teacher_active_assignment_teacher"""
    await state.set_state(ChangeCourse.waiting_course_id)
    await cb.message.answer(
        "Введите ID желаемого задания или '-', если хотите сбросить его."
    )
    await cb.answer()

@teacher_router.message(ChangeCourse.waiting_course_id)
async def process_set_teacher_active_assignment_teacher_second(message: Message, state: FSMContext):
    """Ввод ID курса для функции set_teacher_active_assignment_teacher"""
    assignment_id = message.text
    try:
        async with AsyncSessionLocal() as session:
            if assignment_id == '-':
                await state.update_data(assignment_id=None)
                await message.answer("Задание сброшено", reply_markup=return_to_the_menu())
            else:
                await state.update_data(assignment_id=assignment_id)
                await message.answer("Задание установлено", reply_markup=return_to_the_menu())
    except AccessDenied:
        await message.answer("ID задания написан неправильно или к нему нет доступа", reply_markup=return_to_the_menu())


@teacher_router.callback_query(F.data == "get_course_students_overview_teacher")
async def process_get_course_students_overview_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_course_students_overview_teacher"""
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal() as session:
        overview = await get_course_students_overview(cb.from_user.id, course_id, session)
    await cb.message.answer(await table_to_text(overview), reply_markup=return_to_the_menu())
    await cb.answer()

@teacher_router.callback_query(F.data == "get_assignment_students_status_teacher")
async def process_get_assignment_students_status_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_assignment_students_status_teacher"""
    all_data = await state.get_data()
    assignment_id = all_data.get("assignment_id")
    async with AsyncSessionLocal() as session:
        overview = await get_assignment_students_status(cb.from_user.id, assignment_id, session)
    await cb.message.answer(await table_to_text(overview), reply_markup=return_to_the_menu())
    await cb.answer()


@teacher_router.callback_query(F.data == "get_classroom_users_without_bot_accounts_teacher")
async def process_get_classroom_users_without_bot_accounts_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_classroom_users_without_bot_accounts_teacher"""
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal() as session:
        overview = await get_classroom_users_without_bot_accounts(cb.from_user.id, course_id, session)
    result = ""
    for username in overview:
        result += username + "\n"
    await cb.message.answer(result, reply_markup=return_to_the_menu())
    await cb.answer()


@teacher_router.callback_query(F.data == "get_course_deadlines_overview_teacher")
async def process_get_course_deadlines_overview_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_course_deadlines_overview_teacher"""
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal() as session:
        overview = await get_course_deadlines_overview(cb.from_user.id, course_id, session)
    await cb.message.answer(await table_to_text(overview), reply_markup=return_to_the_menu())
    await cb.answer()


@teacher_router.callback_query(F.data == "get_tasks_to_grade_summary_teacher")
async def process_get_tasks_to_grade_summary_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_tasks_to_grade_summary_teacher"""
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal() as session:
        overview = await get_tasks_to_grade_summary(cb.from_user.id, course_id, session)
    await cb.message.answer(await table_to_text(overview), reply_markup=return_to_the_menu())
    await cb.answer()


@teacher_router.callback_query(F.data == "get_manual_check_submissions_summary_teacher")
async def process_get_manual_check_submissions_summary_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_manual_check_submissions_summary_teacher"""
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal() as session:
        overview = await get_manual_check_submissions_summary(cb.from_user.id, course_id, session)
    await cb.message.answer(await table_to_text(overview), reply_markup=return_to_the_menu())
    await cb.answer()


@teacher_router.callback_query(F.data == "get_teacher_deadline_notification_payload_teacher")
async def process_get_teacher_deadline_notification_payload_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_teacher_deadline_notification_payload_teacher"""
    all_data = await state.get_data()
    assignment_id = all_data.get("assignment_id")
    async with AsyncSessionLocal() as session:
        overview = await get_assignment_students_status(cb.from_user.id, assignment_id, session)
    if overview:
        await cb.message.answer(await table_to_text(overview), reply_markup=return_to_the_menu())
    else:
        await cb.message.answer("Данных нет", reply_markup=return_to_the_menu())
    await cb.answer()

@teacher_router.callback_query(F.data == "add_course_assistant_teacher")
async def process_add_course_assistant_teacher_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции add_course_assistant_teacher"""
    await state.set_state(AddAssistant.waiting_username)
    await cb.message.answer(
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
    except:
        await message.answer("Не получилось добавить ассистента на курс. Возможно, вы некорректно ввели его ник.", reply_markup=return_to_the_menu())


@teacher_router.callback_query(F.data == "remove_course_assistant_teacher")
async def process_remove_course_assistant_teacher_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции remove_course_assistant_teacher"""
    await state.set_state(RemoveAssistant.waiting_username)
    await cb.message.answer(
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
    except:
        await message.answer("Не получилось удалить ассистента с курса. Возможно, вы некорректно ввели его ник.", reply_markup=return_to_the_menu())


@teacher_router.callback_query(F.data == "create_course_announcement_teacher")
async def process_create_course_announcement_teacher_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции create_course_announcement_teacher"""
    await state.set_state(AddAssistant.waiting_username)
    await cb.message.answer(
        "Введите ник ассистента в виде @username или username:"
    )
    await cb.answer()

@teacher_router.message(AddAssistant.waiting_username)
async def process_create_course_announcement_teacher_second(message: Message, state: FSMContext):
    """Ввод имени для функции create_course_announcement_teacher"""
    text = message.text
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        async with AsyncSessionLocal() as session:
            await create_course_announcement(message.from_user.id, course_id, text, session)
        await message.answer("Уведомление успешно создано!", reply_markup=return_to_the_menu())
    except:
        await message.answer("Не получилось создать уведомление.", reply_markup=return_to_the_menu())

@teacher_router.callback_query(F.data == "trigger_manual_sync_for_teacher_teacher")
async def process_get_course_deadlines_overview_teacher(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции trigger_manual_sync_for_teacher_teacher"""
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal() as session:
        done = await trigger_manual_sync_for_teacher(cb.from_user.id, course_id, session)
    if done:
        await cb.message.answer("Сессия синхронизирована")
    else:
        await cb.message.answer("Сессия была обновлена уже 3 раза за сутки. Нет доступа.")
    await cb.answer()

@teacher_router.callback_query(F.data == "add_organisation_teacher")
async def add_organisation_teacher_first(cb: CallbackQuery, state:FSMContext):
    await state.set_state(AddOrganisation.waiting_name)
    await cb.message.answer(
        "Введите название вашей организации."
    )
    await cb.answer()

@teacher_router.message(AddOrganisation.waiting_name)
async def add_organisation_teacher_second(message: Message, state: FSMContext):
    name = message.text
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal as session:
        await add_organisation(message.from_user.id, course_id, name, session)