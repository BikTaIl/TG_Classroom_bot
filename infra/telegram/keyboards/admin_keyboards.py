from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_menu() -> InlineKeyboardMarkup:
    """Основная клавиатура администратора"""
    buttons = [
        [InlineKeyboardButton(text="Выдать роль учителя", callback_data="grant_teacher_role")],
        [InlineKeyboardButton(text="Забрать роль учителя", callback_data="revoke_teacher_role")],
        [InlineKeyboardButton(text="Забанить пользователя", callback_data="ban_user")],
        [InlineKeyboardButton(text="Разбанить пользователя", callback_data="unban_user")],
        [InlineKeyboardButton(text="Сводка ошибок бота", callback_data="get_error_count_for_day")],
        [InlineKeyboardButton(text="Последнее успешное обращение", callback_data="get_last_successful_github_call_time")],
        [InlineKeyboardButton(text="Информация о последнем ошибочном обращении", callback_data="get_last_failed_github_call_info")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def return_to_the_menu() -> InlineKeyboardMarkup:
    """Клавиатура, появляющаяся после успешного запроса/
    успешного выполнения функции и отправляющая в стартовое
    меню или в меню администратора"""
    buttons = [
        [InlineKeyboardButton(text="В меню администратора", callback_data="start_admin")],
        [InlineKeyboardButton(text="В главное меню", callback_data="start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)