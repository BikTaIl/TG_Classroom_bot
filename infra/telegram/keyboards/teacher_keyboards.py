from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_teacher_menu() -> InlineKeyboardMarkup:
    """Основная клавиатура учителя"""
    buttons = [
        [InlineKeyboardButton(text="Установить активный курс", callback_data="set_teacher_active_course_teacher")],
        [InlineKeyboardButton(text="Установить активное задание", callback_data="set_teacher_active_assignment_teacher")],
        [InlineKeyboardButton(text="Сводка по студентам курса", callback_data="get_course_students_overview_teacher")],
        [InlineKeyboardButton(text="Сводка по заданию курса", callback_data="get_assignment_students_status_teacher")],
        [InlineKeyboardButton(text="Github-логины студентов, которых нет в боте", callback_data="get_classroom_users_without_bot_accounts_teacher")],
        [InlineKeyboardButton(text="Сводка всех дедлайнов", callback_data="get_course_deadlines_overview_teacher")],
        [InlineKeyboardButton(text="Сводка по задачам, которые надо оценить", callback_data="get_tasks_to_grade_summary_teacher")],
        [InlineKeyboardButton(text="Сводка по ручной проверке", callback_data="get_manual_check_submissions_summary_teacher")],
        [InlineKeyboardButton(text="Данные для уведомления по сдаче", callback_data="get_teacher_deadline_notification_payload_teacher")],
        [InlineKeyboardButton(text="Добавить ассистента", callback_data="add_course_assistant_teacher")],
        [InlineKeyboardButton(text="Удалить ассистента", callback_data="remove_course_assistant_teacher")],
        [InlineKeyboardButton(text="Создать уведомление для курса", callback_data="create_course_announcement_teacher")],
        [InlineKeyboardButton(text="Выполнить ручную синхронизацию курса", callback_data="trigger_manual_sync_for_teacher_teacher")],
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