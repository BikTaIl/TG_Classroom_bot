from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Any


def get_assistant_menu() -> InlineKeyboardMarkup:
    """Основная клавиатура ассистента"""
    buttons = [
        [InlineKeyboardButton(text="Установить активный курс", callback_data="choose_assistant_active_course")],
        [InlineKeyboardButton(text="Установить активное задание", callback_data="choose_course_students_overview")],
        [InlineKeyboardButton(text="Сводка по заданию курса", callback_data="get_assignment_students_status_assistant")],
        [InlineKeyboardButton(text="Github-логины студентов, которых нет в боте", callback_data="get_classroom_users_without_bot_accounts_assistant")],
        [InlineKeyboardButton(text="Сводка всех дедлайнов", callback_data="get_course_deadlines_overview_assistant")],
        [InlineKeyboardButton(text="Сводка по задачам, которые надо оценить", callback_data="get_tasks_to_grade_summary_assistant")],
        [InlineKeyboardButton(text="Сводка по ручной проверке", callback_data="get_manual_check_submissions_summary_assistant")],
        [InlineKeyboardButton(text="Данные для уведомления по сдаче", callback_data="get_assistant_deadline_notification_payload_assistant")],
        [InlineKeyboardButton(text="Сводки", callback_data="get_summary_assistant")],
        [InlineKeyboardButton(text="Добавить ручную проверку текущему заданию", callback_data="select_manual_check_assignment_assistant")],
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

        [InlineKeyboardButton(text="Установить активный курс", callback_data="set_assistant_active_course"),
        [InlineKeyboardButton(text="В меню учителя", callback_data="start_assistant")],
        [InlineKeyboardButton(text="В главное меню", callback_data="start")]]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def summaries() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Сводка по ручной проверке", callback_data="get_manual_check_submissions_summary_assistant")],
        [InlineKeyboardButton(text="Сводка всех дедлайнов", callback_data="get_course_deadlines_overview_assistant")],
        [InlineKeyboardButton(text="Сводка по задачам, которые надо оценить", callback_data="get_tasks_to_grade_summary_assistant")],
        [InlineKeyboardButton(text="Сводка по студентам курса", callback_data="get_course_students_overview_assistant")],
        [InlineKeyboardButton(text="Сводка по заданию курса", callback_data="get_assignment_students_status_assistant")],
        [InlineKeyboardButton(text="В меню учителя", callback_data="start_assistant")],
        [InlineKeyboardButton(text="В главное меню", callback_data="start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def choose_course(courses: list[tuple[Any, ...]], page: int) -> InlineKeyboardMarkup:
    courses.append((0, "Сбросить курс"))
    pages = (len(courses) + 5) // 6
    if page >= pages:
        page = pages - 1
    buttons = [[InlineKeyboardButton(text=courses[i][1], callback_data=f"set_assistant_active_course:{str(courses[i][0])}") for i in range(page * 6, min((page + 1) * 6, len(courses)))]]
    buttons.append(
        [InlineKeyboardButton(text="Предыдущая страница", callback_data=f"previous_paper_course_assistant:{str(page)}" if page != 0 else ""),
         InlineKeyboardButton(text=f"{str(page + 1)}/{str(pages)}", callback_data=""),
         InlineKeyboardButton(text="Следующая страница", callback_data=f"next_paper_course_assistant:{str(page)}" if page != pages - 1 else "")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def choose_assignment(assignments: list[tuple[Any, ...]], page: int) -> InlineKeyboardMarkup:
    assignments.append((0, "Сбросить курс"))
    pages = (len(assignments) + 5) // 6
    if page >= pages:
        page = pages - 1
    buttons = [[InlineKeyboardButton(text=assignments[i][1], callback_data=f"set_assistant_active_assignment:{str(assignments[i][0])}:{str(assignments[i][0])}") for i in range(page * 6, min((page + 1) * 6, len(assignments)))]]
    buttons.append(
        [InlineKeyboardButton(text="Предыдущая страница", callback_data=f"previous_paper_course_assistant:{str(page)}" if page != 0 else ""),
         InlineKeyboardButton(text=f"{str(page + 1)}/{str(pages)}", callback_data=""),
         InlineKeyboardButton(text="Следующая страница", callback_data=f"next_paper_course_assistant:{str(page)}" if page != pages - 1 else "")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)