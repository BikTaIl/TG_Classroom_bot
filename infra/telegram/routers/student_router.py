import asyncio
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F

from adapters.table_to_text import table_to_text
from infra.db import AsyncSessionLocal
from infra.telegram.keyboards.student_keyboards import *
from .states import *
from commands.student_commands import *

student_router = Router()

@student_router.callback_query(F.data == "start_student")
async def admin_panel(cb: CallbackQuery):
    """Отображение клавиатуры админа"""
    await cb.message.answer("Панель студента:", reply_markup=get_student_menu())
    await cb.answer()

@student_router.callback_query(F.data == "set_student_active_course")
async def process_set_student_active_course_first(cb: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeCourse.waiting_course_id)
    await cb.message.answer(
        "Введите ID желаемого курса или '-', если хотите сбросить курс"
    )
    await cb.answer()

@student_router.message(ChangeCourse.waiting_course_id)
async def process_set_student_active_course_second(message: Message, state: FSMContext):
    course_id = message.text
    try:
        async with AsyncSessionLocal() as session:
            if course_id == '-':
                await set_student_active_course(message.from_user.id, course_id=None, session=session)
                await state.update_data(course_id=None)
                await message.answer("Курс сброшен", reply_markup=return_to_the_menu())
            else:
                await set_student_active_course(message.from_user.id, course_id=course_id, session=session)
                await state.update_data(course_id=course_id)
                await message.answer("Курс установлен", reply_markup=return_to_the_menu())
    except:
        await message.answer("ID курса написан неправильно или к нему нет доступа", reply_markup=return_to_the_menu())


@student_router.callback_query(F.data == "get_student_notification_rules")
async def process_get_student_notification_rules(cb: CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as session:
        rules = await get_student_notification_rules(cb.message.from_user.id, session)
    answer = ""
    for i in len(rules):
        answer += f"Дедлайн {i + 1} наступает за {rules[i]} часов до сдачи \n"
    await cb.message.answer(answer, reply_markup=return_to_the_menu())
    await cb.answer()

@student_router.callback_query(F.data == "add_student_notification_rule")
async def process_add_student_notification_rule_first(cb: CallbackQuery, state: FSMContext):
    await state.set_state(NewDeadline.waiting_hours)
    await cb.message.answer(
        "Введите количество часов, за которое хотите получить уведомление о дедлайне:"
    )
    await cb.answer()


@student_router.message(NewDeadline.waiting_hours)
async def process_add_student_notification_rule_second(message: Message, state: FSMContext):
    hours = message.text
    try:
        hours = int(hours)
        async with AsyncSessionLocal() as session:
            await add_student_notification_rule(message.from_user.id, hours, session)
        await message.answer("Уведомление успешно добавлено!", reply_markup=return_to_the_menu())
        await state.clear()
    except Exception as e:
        if e == TypeError:
            await message.answer("Неправильный формат сообщения. Введите число.")
        else:
            await message.answer("Не получилось добавить уведомление.", reply_markup=return_to_the_menu())
            await state.clear()


@student_router.callback_query(F.data == "remove_student_notification_rule")
async def process_remove_student_notification_rule_first(cb: CallbackQuery, state: FSMContext):
    await state.set_state(RemoveDeadline.waiting_hours)
    await cb.message.answer(
        "Введите количество часов, за которое хотите получить уведомление о дедлайне:"
    )
    await cb.answer()


@student_router.message(RemoveDeadline.waiting_hours)
async def process_remove_student_notification_rule_second(message: Message, state: FSMContext):
    hours = message.text
    try:
        hours = int(hours)
        async with AsyncSessionLocal() as session:
            await remove_student_notification_rule(message.from_user.id, hours, session)
        await message.answer("Уведомление успешно удалено!", reply_markup=return_to_the_menu())
        await state.clear()
    except Exception as e:
        if e == TypeError:
            await message.answer("Неправильный формат сообщения. Введите число.")
        else:
            await message.answer("Не получилось удалить уведомление.", reply_markup=return_to_the_menu())
            await state.clear()


@student_router.callback_query(F.data == "reset_student_notification_rules_to_default")
async def process_reset_student_notification_rules_to_default(cb: CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as session:
        await reset_student_notification_rules_to_default(cb.message.from_user.id, session)
    await cb.message.answer("Настройки уведомлений успешно сброшены!", reply_markup=return_to_the_menu())
    await cb.answer()


@student_router.callback_query(F.data == "get_student_active_assignments_summary")
async def process_get_student_active_assignments_summary(cb: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal() as session:
        result = await table_to_text(await get_student_active_assignments_summary(cb.message.from_user.id, session, course_id))
    await cb.message.answer(f"Сводка всех активных заданий:\n{result}", reply_markup=return_to_the_menu())
    await cb.answer()



@student_router.callback_query(F.data == "get_student_overdue_assignments_summary")
async def process_get_student_overdue_assignments_summary(cb: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal() as session:
        result = await get_student_overdue_assignments_summary(cb.message.from_user.id, session, course_id)
    await cb.message.answer(f"Сводка всех активных заданий:\n{result}", reply_markup=return_to_the_menu())
    await cb.answer()


@student_router.callback_query(F.data == "get_student_grades_summary")
async def process_get_student_grades_summary(cb: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal() as session:
        result = await get_student_grades_summary(cb.message.from_user.id, session, course_id)
    await cb.message.answer(f"Сводка всех активных заданий:\n{result}", reply_markup=return_to_the_menu())
    await cb.answer()


@student_router.callback_query(F.data == "get_student_grades_summary")
async def process_get_student_grades_summary(cb: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    assignment_id = all_data.get("assignment_id")
    async with AsyncSessionLocal() as session:
        result = await get_student_grades_summary(cb.message.from_user.id, session, assignment_id)
    await cb.message.answer(f"Сводка всех активных заданий:\n{result}", reply_markup=return_to_the_menu())
    await cb.answer()


@student_router.callback_query(F.data == "submit_course_feedback")
async def process_submit_course_feedback_first(cb: CallbackQuery, state: FSMContext):
    await state.set_state(SendMessage.waiting_message)
    await cb.message.answer(
        "Введите сообщение, которое хотите отправить:"
    )
    await cb.answer()

@student_router.message(SendMessage.waiting_message)
async def process_submit_course_feedback_second(message: Message, state: FSMContext):
    await state.update_data(message=message.text)
    await state.clear()
    await message.answer(
        "Хотите ли вы, чтобы сообщение было анонимным?", reply_markup=is_anonymus()
    )

@student_router.callback_query(F.data == "is_anonymus")
async def process_submit_course_feedback_anonymus(cb: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    message_send = all_data.get("message")
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal() as session:
        await submit_course_feedback(cb.message.from_user.id, course_id, message_send, True, session)
    await cb.message.answer("Сообщение отправлено!", reply_markup=return_to_the_menu())
    await cb.anwer()

@student_router.callback_query(F.data == "is_not_anonymus")
async def process_submit_course_feedback_anonymus(cb: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    message_send = all_data.get("message")
    course_id = all_data.get("course_id")
    async with AsyncSessionLocal() as session:
        await submit_course_feedback(cb.message.from_user.id, course_id, message_send, False, session)
    await cb.message.answer("Сообщение отправлено!", reply_markup=return_to_the_menu())
    await cb.anwer()