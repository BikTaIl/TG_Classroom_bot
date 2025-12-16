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
    """Отображение клавиатуры админа"""
    await cb.message.answer("Панель ассистента:", reply_markup=get_assistant_menu())
    await cb.answer()

@assistant_router.callback_query(F.data == "set_teacher_active_course_assistant")
async def process_set_teacher_active_course_assistant_first(cb: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeCourse.waiting_course_id)
    await cb.message.answer(
        "Введите ID желаемого курса или '-', если хотите сбросить курс"
    )
    await cb.answer()

@assistant_router.message(ChangeCourse.waiting_course_id)
async def process_set_teacher_active_course_assistant_second(message: Message, state: FSMContext):
    course_id = message.text
    try:
        async with AsyncSessionLocal() as session:
            if course_id == '-':
                await set_teacher_active_course(message.from_user.id, course_id=None, session=session)
                await state.update_data(course_id=None)
                await message.answer("Курс сброшен", reply_markup=return_to_the_menu())
            else:
                await set_teacher_active_course(message.from_user.id, course_id=course_id, session=session)
                await state.update_data(course_id=course_id)
                await message.answer("Курс установлен", reply_markup=return_to_the_menu())
    except:
        await message.answer("ID курса написан неправильно или к нему нет доступа", reply_markup=return_to_the_menu())


@assistant_router.callback_query(F.data == "set_teacher_active_assignment_assistant")
async def process_set_teacher_active_assignment_assistant_first(cb: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeCourse.waiting_course_id)
    await cb.message.answer(
        "Введите ID желаемого задания или '-', если хотите сбросить его."
    )
    await cb.answer()

@assistant_router.message(ChangeCourse.waiting_course_id)
async def process_set_teacher_active_assignment_assistant_second(message: Message, state: FSMContext):
    assignment_id = message.text
    try:
        async with AsyncSessionLocal() as session:
            if assignment_id == '-':
                await set_teacher_active_assignment(message.from_user.id, assignment_id=None, session=session)
                await state.update_data(assignment_id=None)
                await message.answer("Задание сброшено", reply_markup=return_to_the_menu())
            else:
                await set_teacher_active_assignment(message.from_user.id, assignment_id=assignment_id, session=session)
                await state.update_data(assignment_id=assignment_id)
                await message.answer("Задание установлено", reply_markup=return_to_the_menu())
    except:
        await message.answer("ID задания написан неправильно или к нему нет доступа", reply_markup=return_to_the_menu())


@assistant_router.callback_query(F.data == "get_course_students_overview_assistant")
async def process_get_course_students_overview_assistant(cb: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal() as session:
        overview = await get_course_students_overview(cb.from_user.id, course_id, session)
    await cb.message.answer(await table_to_text(overview), reply_markup=return_to_the_menu())
    await cb.answer()

@assistant_router.callback_query(F.data == "get_assignment_students_status_assistant")
async def process_get_assignment_students_status_assistant(cb: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    assignment_id = all_data.get("assignment_id")
    async with AsyncSessionLocal() as session:
        overview = await get_assignment_students_status(cb.from_user.id, assignment_id, session)
    await cb.message.answer(await table_to_text(overview), reply_markup=return_to_the_menu())
    await cb.answer()


@assistant_router.callback_query(F.data == "get_classroom_users_without_bot_accounts_assistant")
async def process_get_classroom_users_without_bot_accounts_assistant(cb: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal() as session:
        overview = await get_classroom_users_without_bot_accounts(cb.from_user.id, course_id, session)
    result = ""
    for username in overview:
        result += username + "\n"
    await cb.message.answer(result, reply_markup=return_to_the_menu())
    await cb.answer()


@assistant_router.callback_query(F.data == "get_course_deadlines_overview_assistant")
async def process_get_course_deadlines_overview_assistant(cb: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal() as session:
        overview = await get_course_deadlines_overview(cb.from_user.id, course_id, session)
    await cb.message.answer(await table_to_text(overview), reply_markup=return_to_the_menu())
    await cb.answer()


@assistant_router.callback_query(F.data == "get_tasks_to_grade_summary_assistant")
async def process_get_tasks_to_grade_summary_assistant(cb: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal() as session:
        overview = await get_tasks_to_grade_summary(cb.from_user.id, course_id, session)
    await cb.message.answer(await table_to_text(overview), reply_markup=return_to_the_menu())
    await cb.answer()


@assistant_router.callback_query(F.data == "get_manual_check_submissions_summary_assistant")
async def process_get_manual_check_submissions_summary_assistant(cb: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal() as session:
        overview = await get_manual_check_submissions_summary(cb.from_user.id, course_id, session)
    await cb.message.answer(await table_to_text(overview), reply_markup=return_to_the_menu())
    await cb.answer()


@assistant_router.callback_query(F.data == "get_teacher_deadline_notification_payload_assistant")
async def process_get_teacher_deadline_notification_payload_assistant(cb: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    assignment_id = all_data.get("assignment_id")
    async with AsyncSessionLocal() as session:
        overview = await get_assignment_students_status(cb.from_user.id, assignment_id, session)
    if overview:
        await cb.message.answer(await table_to_text(overview), reply_markup=return_to_the_menu())
    else:
        await cb.message.answer("Данных нет")
    await cb.answer()