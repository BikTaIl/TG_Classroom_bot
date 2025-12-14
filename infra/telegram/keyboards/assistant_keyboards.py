from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_assistant_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Установить активный курс", callback_data="set_teacher_active_course_assistant")],
        [InlineKeyboardButton(text="Установить активное задание", callback_data="set_teacher_active_assignment_assistant")],
        [InlineKeyboardButton(text="Сводка по студентам курса", callback_data="get_course_students_overview_assistant")],
        [InlineKeyboardButton(text="Сводка по заданию курса", callback_data="get_assignment_students_status_assistant")],
        [InlineKeyboardButton(text="Github-логины студентов, которых нет в боте", callback_data="get_classroom_users_without_bot_accounts_assistant")],
        [InlineKeyboardButton(text="Сводка всех дедлайнов", callback_data="get_course_deadlines_overview_assistant")],
        [InlineKeyboardButton(text="Сводка по задачам, которые надо оценить", callback_data="get_tasks_to_grade_summary_assistant")],
        [InlineKeyboardButton(text="Сводка по ручной проверке", callback_data="get_manual_check_submissions_summary_assistant")],
        [InlineKeyboardButton(text="Данные для уведомления по сдаче", callback_data="get_teacher_deadline_notification_payload_assistant")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def return_to_the_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="В меню ассистента", callback_data="start_assistant")],
        [InlineKeyboardButton(text="В главное меню", callback_data="start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)