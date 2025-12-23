from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Any


def get_teacher_menu() -> InlineKeyboardMarkup:
    """Основная клавиатура учителя"""
    buttons = [
        [InlineKeyboardButton(text="Установить активный курс", callback_data="choose_teacher_active_course")],
        [InlineKeyboardButton(text="Установить активное задание", callback_data="choose_teacher_active_assignment")],
        [InlineKeyboardButton(text="Github-логины студентов, которых нет в боте", callback_data="get_classroom_users_without_bot_accounts_teacher")],
        [InlineKeyboardButton(text="Данные для уведомления по сдаче", callback_data="get_teacher_deadline_notification_payload_teacher")],
        [InlineKeyboardButton(text="Добавить ассистента", callback_data="add_course_assistant_teacher")],
        [InlineKeyboardButton(text="Удалить ассистента", callback_data="remove_course_assistant_teacher")],
        [InlineKeyboardButton(text="Создать уведомление для курса", callback_data="create_course_announcement_teacher")],
        [InlineKeyboardButton(text="Выполнить ручную синхронизацию курса", callback_data="trigger_manual_sync_for_teacher_teacher")],
        [InlineKeyboardButton(text="Добавить ручную проверку текущему заданию", callback_data="select_manual_check_assignment_teacher")],
        [InlineKeyboardButton(text="Сводки", callback_data="get_summary_teacher")],
        [InlineKeyboardButton(text="В главное меню", callback_data="start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def return_to_the_menu() -> InlineKeyboardMarkup:
    """Клавиатура, появляющаяся после успешного запроса/
    успешного выполнения функции и отправляющая в стартовое
    меню или в меню учителя"""
    buttons = [
        [InlineKeyboardButton(text="В меню учителя", callback_data="start_teacher")],
        [InlineKeyboardButton(text="В главное меню", callback_data="start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def have_to_choose_course() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Установить активный курс", callback_data="choose_teacher_active_course")],
        [InlineKeyboardButton(text="В меню учителя", callback_data="start_teacher")],
        [InlineKeyboardButton(text="В главное меню", callback_data="start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def have_to_choose_assignment() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Установить активное задание", callback_data="choose_teacher_active_assignment")],
        [InlineKeyboardButton(text="В меню учителя", callback_data="start_teacher")],
        [InlineKeyboardButton(text="В главное меню", callback_data="start")]
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
    courses.append((0, "Сбросить курс"))
    pages = (len(courses) + 5) // 6
    buttons = [[InlineKeyboardButton(text=courses[i][1], callback_data=f"set_teacher_active_course:{str(courses[i][0])}")] for i in range(page * 6, min((page + 1) * 6, len(courses)))]
    if page > 0:
        buttons.append(
            [InlineKeyboardButton(text="Предыдущая страница",
                                 callback_data=f"previous_paper_course_teacher:{str(page)}")]
        )
    if page < pages - 1:
        buttons.append(
            [InlineKeyboardButton(text="Следующая страница", callback_data=f"next_paper_course_teacher:{str(page)}" )]
        )
    buttons.append([InlineKeyboardButton(text="В меню учителя", callback_data="start_teacher")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def choose_assignment(assignments: list[tuple[Any, ...]], page: int) -> InlineKeyboardMarkup:
    assignments.append((0, "Сбросить задание"))
    pages = (len(assignments) + 5) // 6
    buttons = [[InlineKeyboardButton(text=assignments[i][1], callback_data=f"set_teacher_active_assignment:{str(assignments[i][0])}")] for i in range(page * 6, min((page + 1) * 6, len(assignments)))]
    if page > 0:
        buttons.append(
            [InlineKeyboardButton(text="Предыдущая страница",
                                  callback_data=f"previous_paper_assignment_teacher:{str(page)}")]
        )
    if page < pages - 1:
        buttons.append(
            [InlineKeyboardButton(text="Следующая страница", callback_data=f"next_paper_assignment_teacher:{str(page)}")]
        )
    buttons.append([InlineKeyboardButton(text="В меню учителя", callback_data="start_teacher")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)