from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F

from adapters.table_to_text import table_to_text
from infra.db import AsyncSessionLocal
from infra.telegram.keyboards.student_keyboards import *
from .states import *
from commands.student_commands import *
from commands.teacher_and_assistant_commands import find_course, find_assignment

student_router = Router()

@student_router.callback_query(F.data == "start_student")
async def admin_panel(cb: CallbackQuery):
    """Функция отображения панели студента.
       Отображается только по кнопке, через команду зайти нельзя."""
    await cb.message.answer("Панель студента:", reply_markup=get_student_menu())
    await cb.answer()

@student_router.callback_query(F.data == "set_student_active_course")
async def process_set_student_active_course_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции set_student_active_course"""
    await state.set_state(ChangeCourse.waiting_course_name)
    await cb.message.update_text(
        "Введите название желаемого курса или '-', если хотите сбросить курс"
    )
    await cb.answer()

@student_router.message(ChangeCourse.waiting_course_name)
async def process_set_student_active_course_second(message: Message, state: FSMContext):
    """Ввод ID курса для функции set_student_active_course"""
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


@student_router.callback_query(F.data == "get_student_notification_rules")
async def process_get_student_notification_rules(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_student_notification_rules"""
    try:
        async with AsyncSessionLocal() as session:
            rules = await get_student_notification_rules(cb.from_user.id, session)
        answer = ""
        for i in range(len(rules)):
            answer += f"Дедлайн {i + 1} наступает за {rules[i]} часов до сдачи \n"
        await cb.message.update_text(answer, reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@student_router.callback_query(F.data == "add_student_notification_rule")
async def process_add_student_notification_rule_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции add_student_notification_rule"""
    await state.set_state(NewDeadline.waiting_hours)
    await cb.message.update_text(
        "Введите количество часов, за которое хотите получить уведомление о дедлайне:"
    )
    await cb.answer()


@student_router.message(NewDeadline.waiting_hours)
async def process_add_student_notification_rule_second(message: Message, state: FSMContext):
    """Ввод количества часов перед дедлайном для уведомления для функции add_student_notification_rule"""
    hours = message.text
    try:
        hours = int(hours)
        async with AsyncSessionLocal() as session:
            await add_student_notification_rule(message.from_user.id, hours, session)
        await message.answer("Уведомление успешно добавлено!", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
        await state.clear()
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
        await state.clear()
    except TypeError:
        await message.answer("Неправильный формат сообщения. Попробуйте еще раз и введите число", reply_markup=return_to_the_menu())


@student_router.callback_query(F.data == "remove_student_notification_rule")
async def process_remove_student_notification_rule_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции remove_student_notification_rule"""
    await state.set_state(RemoveDeadline.waiting_hours)
    await cb.message.update_text(
        "Введите количество часов, за которое перед дедлайном стоит уведомление, необходимое к удалению:"
    )
    await cb.answer()


@student_router.message(RemoveDeadline.waiting_hours)
async def process_remove_student_notification_rule_second(message: Message, state: FSMContext):
    """Ввод количества часов перед дедлайном для уведомления для функции remove_student_notification_rule"""
    hours = message.text
    try:
        hours = int(hours)
        async with AsyncSessionLocal() as session:
            await remove_student_notification_rule(message.from_user.id, hours, session)
        await message.answer("Уведомление успешно удалено!", reply_markup=return_to_the_menu())
        await state.clear()
    except AccessDenied as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
        await state.clear()
    except ValueError as err:
        await message.answer(str(err), reply_markup=return_to_the_menu())
        await state.clear()
    except TypeError:
        await message.answer("Неправильный формат сообщения. Попробуйте еще раз и введите число", reply_markup=return_to_the_menu())


@student_router.callback_query(F.data == "reset_student_notification_rules_to_default")
async def process_reset_student_notification_rules_to_default(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции reset_student_notification_rules_to_default"""
    async with AsyncSessionLocal() as session:
        await reset_student_notification_rules_to_default(cb.from_user.id, session)
    await cb.message.update_text("Настройки уведомлений успешно сброшены!", reply_markup=return_to_the_menu())
    await cb.answer()


@student_router.callback_query(F.data == "get_student_active_assignments_summary")
async def process_get_student_active_assignments_summary(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_student_active_assignments_summary"""
    all_data = await state.get_data()
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            course_id = await find_course(cb.from_user.id, course_name, session)
            result = await table_to_text(await get_student_active_assignments_summary(cb.from_user.id, course_id, session))
        await cb.message.update_text(f"Сводка всех активных заданий:\n{result}", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()



@student_router.callback_query(F.data == "get_student_overdue_assignments_summary")
async def process_get_student_overdue_assignments_summary(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_student_overdue_assignments_summary"""
    all_data = await state.get_data()
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            course_id = await find_course(cb.from_user.id, course_name, session)
            result = await get_student_overdue_assignments_summary(cb.from_user.id, course_id,  session)
        await cb.message.update_text(f"Сводка всех активных заданий:\n{result}", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()


@student_router.callback_query(F.data == "get_student_grades_summary")
async def process_get_student_grades_summary(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_student_grades_summary"""
    all_data = await state.get_data()
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            course_id = await find_course(cb.from_user.id, course_name, session)
            result = await get_student_grades_summary(cb.from_user.id, course_id, session)
        await cb.message.update_text(f"Сводка всех активных заданий:\n{result}", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()


@student_router.callback_query(F.data == "get_student_grades_summary")
async def process_get_student_grades_summary(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_student_grades_summary"""
    all_data = await state.get_data()
    assignment_name = all_data.get("assignment_name")
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            assignment_id = await find_assignment(str(await find_course(cb.from_user.id, course_name, session)), assignment_name, session)
            result = await get_student_grades_summary(cb.from_user.id, assignment_id, session)
        await cb.message.update_text(f"Сводка всех активных заданий:\n{result}", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.update_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()


@student_router.callback_query(F.data == "submit_course_feedback")
async def process_submit_course_feedback_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции submit_course_feedback"""
    await state.set_state(SendMessage.waiting_message)
    await cb.message.update_text(
        "Введите сообщение, которое хотите отправить:"
    )
    await cb.answer()

@student_router.message(SendMessage.waiting_message)
async def process_submit_course_feedback_second(message: Message, state: FSMContext):
    """Ввод сообщения для функции submit_course_feedback"""
    await state.update_data(message=message.text)
    await state.clear()
    await message.answer(
        "Хотите ли вы, чтобы сообщение было анонимным?", reply_markup=is_anonymus()
    )

@student_router.callback_query(F.data == "is_anonymus")
async def process_submit_course_feedback_anonymus(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции is_anonymus"""
    all_data = await state.get_data()
    message_send = all_data.get("message")
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            course_id = await find_course(cb.from_user.id, course_name, session)
            await submit_course_feedback(cb.from_user.id, course_id, message_send, True, session)
        await cb.message.answer("Сообщение отправлено!", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.answer(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.answer(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@student_router.callback_query(F.data == "is_not_anonymus")
async def process_submit_course_feedback_not_anonymus(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции is_not_anonymus"""
    all_data = await state.get_data()
    message_send = all_data.get("message")
    all_data.update(message=None)
    course_name = all_data.get("course_name")
    try:
        async with AsyncSessionLocal() as session:
            course_id = await find_course(cb.from_user.id, course_name, session)
            teacher_id = await submit_course_feedback(cb.from_user.id, course_id, message_send, False, session)
        await cb.bot.send_message(teacher_id, message_send)
        await cb.message.answer("Сообщение отправлено!", reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.answer(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.answer(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()