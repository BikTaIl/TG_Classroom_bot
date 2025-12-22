from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Any


def get_assistant_menu() -> InlineKeyboardMarkup:
    """Основная клавиатура ассистента"""
    buttons = [
        [InlineKeyboardButton(text="Установить активный курс", callback_data="choose_teacher_active_course_assistant")],
        [InlineKeyboardButton(text="Установить активное задание", callback_data="choose_course_students_overview_assistant")],
        [InlineKeyboardButton(text="Сводка по заданию курса", callback_data="get_assignment_students_status_assistant")],
        [InlineKeyboardButton(text="Github-логины студентов, которых нет в боте", callback_data="get_classroom_users_without_bot_accounts_assistant")],
        [InlineKeyboardButton(text="Сводка всех дедлайнов", callback_data="get_course_deadlines_overview_assistant")],
        [InlineKeyboardButton(text="Сводка по задачам, которые надо оценить", callback_data="get_tasks_to_grade_summary_assistant")],
        [InlineKeyboardButton(text="Сводка по ручной проверке", callback_data="get_manual_check_submissions_summary_assistant")],
        [InlineKeyboardButton(text="Данные для уведомления по сдаче", callback_data="get_teacher_deadline_notification_payload_assistant")],
        [InlineKeyboardButton(text="Сводки", callback_data="get_summary_assistant")],
        [InlineKeyboardButton(text="В главное меню", callback_data="start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def return_to_the_menu() -> InlineKeyboardMarkup:
    """Клавиатура, появляющаяся после успешного запроса/
    успешного выполнения функции и отправляющая в стартовое
    меню или в меню ассистента"""
    buttons = [
        [InlineKeyboardButton(text="В меню ассистента", callback_data="start_assistant")],
        [InlineKeyboardButton(text="В главное меню", callback_data="start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def have_to_choose_course() -> InlineKeyboardMarkup:
    buttons = [

        [InlineKeyboardButton(text="Установить активный курс", callback_data="set_teacher_active_course_teacher"),
        [InlineKeyboardButton(text="В меню учителя", callback_data="start_teacher")],
        [InlineKeyboardButton(text="В главное меню", callback_data="start")]]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def summaries() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Сводка по ручной проверке", callback_data="get_manual_check_submissions_summary_teacher")],
        [InlineKeyboardButton(text="Сводка всех дедлайнов", callback_data="get_course_deadlines_overview_teacher")],
        [InlineKeyboardButton(text="Сводка по задачам, которые надо оценить", callback_data="get_tasks_to_grade_summary_teacher")],
        [InlineKeyboardButton(text="Сводка по студентам курса", callback_data="get_course_students_overview_teacher")],
        [InlineKeyboardButton(text="Сводка по заданию курса", callback_data="get_assignment_students_status_teacher")],
        [InlineKeyboardButton(text="В меню учителя", callback_data="start_teacher")],
        [InlineKeyboardButton(text="В главное меню", callback_data="start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def choose_course(courses: list[tuple[Any, ...]], page: int) -> InlineKeyboardMarkup:
    pages = (len(courses) + 5) // 6
    courses.append(("Сбросить курс", 0))
    if page >= pages:
        page = pages - 1
    buttons = [[InlineKeyboardButton(text=courses[i][0], callback_data=f"set_teacher_active_course:{str(courses[i][0])}") for i in range(page * 6, min((page + 1) * 6, len(courses)))]]
    buttons.append(
        [InlineKeyboardButton(text="Предыдущая страница", callback_data=f"previous_paper_course_teacher:{page}" if page != 0 else ""),
         InlineKeyboardButton(text=f"{page + 1}/{pages}"),
         InlineKeyboardButton(text="Следующая страница", callback_data=f"next_paper_course_teacher:{page}" if page != pages - 1 else "")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def choose_assignment(assignments: list[tuple[Any, ...]], page: int) -> InlineKeyboardMarkup:
    pages = (len(assignments) + 5) // 6
    assignments.append(("Сбросить курс", 0))
    if page >= pages:
        page = pages - 1
    buttons = [[InlineKeyboardButton(text=assignments[i][0], callback_data=f"set_teacher_active_course:{str(assignments[i][0])}:{str(assignments[i][1])}") for i in range(page * 6, min((page + 1) * 6, len(assignments)))]]
    buttons.append(
        [InlineKeyboardButton(text="Предыдущая страница", callback_data=f"previous_paper_course_teacher:{page}" if page != 0 else ""),
         InlineKeyboardButton(text=f"{page + 1}/{pages}"),
         InlineKeyboardButton(text="Следующая страница", callback_data=f"next_paper_course_teacher:{page}" if page != pages - 1 else "")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)