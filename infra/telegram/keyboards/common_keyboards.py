from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_start_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Вернуть URL для привязки GitHub", callback_data="login_link_github")],
        [InlineKeyboardButton(text="Разлогинить текущий аккаунт из GitHub", callback_data="logout_user")],
        [InlineKeyboardButton(text="Выбрать активную роль", callback_data="set_active_role")],
        [InlineKeyboardButton(text="Глобально сменить рычажок уведомлений по дд для пользователя", callback_data="toggle_global_notifications")],
        [InlineKeyboardButton(text="Сменить гитхаб-аккаунт на другой залогиненный", callback_data="change_git_account")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def choose_role() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Студент", callback_data="change_role_student"),
        InlineKeyboardButton(text="Учитель", callback_data="change_role_teacher")],
        [InlineKeyboardButton(text="Ассистент", callback_data="change_role_assistant"),
        InlineKeyboardButton(text="Администратор", callback_data="change_role_admin")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def return_to_the_start() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Вернуться на главную панель", callback_data="start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def go_to_admin() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Перейти на панель администратора", callback_data="start_admin")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def go_to_teacher() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Перейти на панель учителя", callback_data="start_teacher")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def go_to_assistant() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Перейти на панель ассистента", callback_data="start_assistant")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)