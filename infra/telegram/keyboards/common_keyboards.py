from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_start_menu() -> InlineKeyboardMarkup:
    """Основная клавиатура стартового меню"""
    buttons = [
        [InlineKeyboardButton(text="Вернуть URL для привязки GitHub", callback_data="login_link_github")],
        [InlineKeyboardButton(text="Разлогинить текущий аккаунт из GitHub", callback_data="logout_user")],
        [InlineKeyboardButton(text="Выбрать активную роль", callback_data="set_active_role")],
        [InlineKeyboardButton(text="Глобально сменить рычажок уведомлений по дд для пользователя", callback_data="toggle_global_notifications")],
        [InlineKeyboardButton(text="Сменить гитхаб-аккаунт на другой залогиненный", callback_data="change_git_account")],
        [InlineKeyboardButton(text="Ввести/изменить ФИО", callback_data="enter_name")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def choose_role() -> InlineKeyboardMarkup:
    """Клавиатура для выбора роли, к которой
    пользователь хочет получить доступ"""
    buttons = [
        [InlineKeyboardButton(text="Студент", callback_data="change_role_student"),
        InlineKeyboardButton(text="Учитель", callback_data="change_role_teacher")],
        [InlineKeyboardButton(text="Ассистент", callback_data="change_role_assistant"),
        InlineKeyboardButton(text="Администратор", callback_data="change_role_admin")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def return_to_the_start() -> InlineKeyboardMarkup:
    """Возвращение в стартовое меню после успешного запроса/
    успешного выполнения функции"""
    buttons = [
        [InlineKeyboardButton(text="Вернуться в главное меню", callback_data="start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def go_to_admin() -> InlineKeyboardMarkup:
    """Кнопка для перехода в меню администратора
    после проверки доступа"""
    buttons = [
        [InlineKeyboardButton(text="Перейти в меню администратора", callback_data="start_admin")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def go_to_teacher() -> InlineKeyboardMarkup:
    """Кнопка для перехода в меню учителя
    после проверки доступа"""
    buttons = [
        [InlineKeyboardButton(text="Перейти в меню учителя", callback_data="start_teacher")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def go_to_assistant() -> InlineKeyboardMarkup:
    """Кнопка для перехода в меню ассистента
    после проверки доступа"""
    buttons = [
        [InlineKeyboardButton(text="Перейти в меню ассистента", callback_data="start_assistant")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def go_to_student() -> InlineKeyboardMarkup:
    """Кнопка для перехода в меню студента
    после проверки доступа"""
    buttons = [
        [InlineKeyboardButton(text="Перейти в меню студента", callback_data="start_student")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def registration_url(url: str) -> InlineKeyboardMarkup:
    """Кнопка для перехода по ссылке для авторизации
    аккаунта GitHub"""
    buttons = [
        [InlineKeyboardButton(text="Пройти авторизацию по ссылке:", url=url)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)