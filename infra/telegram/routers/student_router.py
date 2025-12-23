from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F

from adapters.table_to_text import table_to_text
from infra.db import AsyncSessionLocal
from infra.telegram.keyboards.student_keyboards import *
from .states import *
from commands.student_commands import *
from commands.teacher_and_assistant_commands import find_assignments_by_course_id

student_router = Router()

@student_router.callback_query(F.data == "start_student")
async def admin_panel(cb: CallbackQuery):
    """Функция отображения панели студента.
       Отображается только по кнопке, через команду зайти нельзя."""
    await cb.message.answer("Панель студента:", reply_markup=get_student_menu())
    await cb.answer()

@student_router.callback_query(F.data == "choose_student_active_course")
async def process_choose_student_active_course(cb: CallbackQuery, state: FSMContext):
    try:
        async with AsyncSessionLocal() as session:
            courses = await find_students_courses(cb.from_user.id, session)
        await cb.message.edit_text("Выберите курс или сбросьте его:", reply_markup=choose_course(courses, 0))
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@student_router.callback_query(F.data.startswith("set_student_active_course"))
async def process_set_student_active_course(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split(":")
    course_id = int(data[0])
    try:
        if course_id == 0:
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

@student_router.callback_query(F.data.startswith("previous_paper_course_student"))
async def process_previous_page(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split(":")
    page = int(data[1])
    try:
        async with AsyncSessionLocal() as session:
            courses = await find_students_courses(cb.from_user.id, session)
        await cb.message.edit_text("Выберите курс:", reply_markup=choose_course(courses, page - 1))
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@student_router.callback_query(F.data.startswith("next_paper_course_student"))
async def process_next_page(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split(":")
    page = int(data[1])
    try:
        async with AsyncSessionLocal() as session:
            courses = await find_students_courses(cb.from_user.id, session)
        await cb.message.edit_text("Выберите курс:", reply_markup=choose_course(courses, page + 1))
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@student_router.callback_query(F.data == "choose_student_active_assignment")
async def process_choose_student_active_assignment(cb: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        if course_id:
            async with AsyncSessionLocal() as session:
                assignments = await find_assignments_by_course_id(course_id, session)
                print(assignments)
            await cb.message.edit_text("Выберите задание или сбростье его:", reply_markup=choose_assignment(assignments, 0))
        else:
            await cb.message.edit_text("Чтобы выбрать активное задание, нужно выбрать активный курс.", reply_markup=have_to_choose_course())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@student_router.callback_query(F.data.startswith("set_student_active_assignment"))
async def process_set_student_active_assignment(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split(":")
    assignment_id = int(data[1])
    try:
        if assignment_id == 0:
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

@student_router.callback_query(F.data.startswith("previous_paper_assignment_student"))
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

@student_router.callback_query(F.data.startswith("next_paper_assignment_student"))
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

@student_router.callback_query(F.data == "get_student_notification_rules")
async def process_get_student_notification_rules(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_student_notification_rules"""
    try:
        async with AsyncSessionLocal() as session:
            rules = await get_student_notification_rules(cb.from_user.id, session)
        answer = ""
        for i in range(len(rules)):
            answer += f"Дедлайн {i + 1} наступает за {rules[i]} часов до сдачи \n"
        await cb.message.edit_text(answer, reply_markup=return_to_the_menu())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()

@student_router.callback_query(F.data == "add_student_notification_rule")
async def process_add_student_notification_rule_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции add_student_notification_rule"""
    await state.set_state(NewDeadline.waiting_hours)
    await cb.message.edit_text(
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
    finally:
        await state.clear()


@student_router.callback_query(F.data == "remove_student_notification_rule")
async def process_remove_student_notification_rule_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции remove_student_notification_rule"""
    await state.set_state(RemoveDeadline.waiting_hours)
    await cb.message.edit_text(
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
    finally:
        await state.clear()


@student_router.callback_query(F.data == "reset_student_notification_rules_to_default")
async def process_reset_student_notification_rules_to_default(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции reset_student_notification_rules_to_default"""
    async with AsyncSessionLocal() as session:
        await reset_student_notification_rules_to_default(cb.from_user.id, session)
    await cb.message.edit_text("Настройки уведомлений успешно сброшены!", reply_markup=return_to_the_menu())
    await cb.answer()


@student_router.callback_query(F.data == "get_student_active_assignments_summary")
async def process_get_student_active_assignments_summary(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_student_active_assignments_summary"""
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        if course_id:
            async with AsyncSessionLocal() as session:
                result = await table_to_text(await get_student_active_assignments_summary(cb.from_user.id, course_id, session))
            await cb.message.edit_text(f"Сводка всех активных заданий:\n{result}", reply_markup=return_to_the_menu())
        else:
            await cb.message.edit_text("Для получения данных о курсе нужно выбрать активный курс.", reply_markup=have_to_choose_course())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()



@student_router.callback_query(F.data == "get_student_overdue_assignments_summary")
async def process_get_student_overdue_assignments_summary(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_student_overdue_assignments_summary"""
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        if course_id:
            async with AsyncSessionLocal() as session:
                result = await get_student_overdue_assignments_summary(cb.from_user.id, course_id,  session)
            await cb.message.edit_text(f"Сводка всех активных заданий:\n{result}", reply_markup=return_to_the_menu())
        else:
            await cb.message.edit_text("Для получения данных о курсе нужно выбрать активный курс.", reply_markup=have_to_choose_course())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()


@student_router.callback_query(F.data == "get_student_grades_summary")
async def process_get_student_grades_summary(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_student_grades_summary"""
    all_data = await state.get_data()
    course_id = all_data.get("course_id")
    try:
        if course_id:
            async with AsyncSessionLocal() as session:
                result = await get_student_grades_summary(cb.from_user.id, course_id, session)
            await cb.message.edit_text(f"Сводка всех активных заданий:\n{result}", reply_markup=return_to_the_menu())
        else:
            await cb.message.edit_text("Для получения данных о курсе нужно выбрать активный курс.", reply_markup=have_to_choose_course())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()


@student_router.callback_query(F.data == "get_student_grades_summary")
async def process_get_student_grades_summary(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции get_student_grades_summary"""
    all_data = await state.get_data()
    assignment_id = all_data.get("assignment_id")
    try:
        if assignment_id:
            async with AsyncSessionLocal() as session:
                result = await get_student_grades_summary(cb.from_user.id, assignment_id, session)
            await cb.message.edit_text(f"Сводка всех активных заданий:\n{result}", reply_markup=return_to_the_menu())
        else:
            await cb.message.edit_text("Для получения данных о задании нужно выбрать активный курс.", reply_markup=have_to_choose_assignment())
    except AccessDenied as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.edit_text(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()


@student_router.callback_query(F.data == "submit_course_feedback")
async def process_submit_course_feedback_first(cb: CallbackQuery, state: FSMContext):
    """Запуск по кнопке функции submit_course_feedback"""
    await state.set_state(SendMessage.waiting_message)
    await cb.message.edit_text(
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
    course_id = all_data.get("course_id")
    try:
        if course_id:
            async with AsyncSessionLocal() as session:
                await submit_course_feedback(cb.from_user.id, course_id, message_send, True, session)
            await cb.message.answer("Сообщение отправлено!", reply_markup=return_to_the_menu())
        else:
            await cb.message.edit_text("Для получения данных о курсе нужно выбрать активный курс.", reply_markup=have_to_choose_course())
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
    course_id = all_data.get("course_id")
    try:
        if course_id:
            async with AsyncSessionLocal() as session:
                student_id = await submit_course_feedback(cb.from_user.id, course_id, message_send, False, session)
            await cb.bot.send_message(student_id, message_send)
            await cb.message.answer("Сообщение отправлено!", reply_markup=return_to_the_menu())
        else:
            await cb.message.edit_text("Для получения данных о курсе нужно выбрать активный курс.", reply_markup=have_to_choose_course())
    except AccessDenied as err:
        await cb.message.answer(str(err), reply_markup=return_to_the_menu())
    except ValueError as err:
        await cb.message.answer(str(err), reply_markup=return_to_the_menu())
    finally:
        await cb.answer()