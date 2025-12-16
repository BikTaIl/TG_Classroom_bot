from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm.base import state_class_str


class AddTeacher(StatesGroup):
    """Состояния для добавления преподавателя"""
    waiting_username = State()

class AddAssistant(StatesGroup):
    """Состояния для добавления ассистента"""
    waiting_username = State()

class RemoveTeacher(StatesGroup):
    """Состояния для удаления преподавателя"""
    waiting_username = State()

class RemoveAssistant(StatesGroup):
    """Состояния для удаления ассистента"""
    waiting_username = State()

class Ban(StatesGroup):
    """Состояния для бана"""
    waiting_username = State()

class Unban(StatesGroup):
    """Состояния для разбана"""
    waiting_username = State()

class FindErrors(StatesGroup):
    waiting_date = State()

class ChangeRole(StatesGroup):
    waiting_role = State()

class ChangeGitHubAccount(StatesGroup):
    waiting_login = State()

class ChangeCourse(StatesGroup):
    waiting_course_id = State()

class NewDeadline(StatesGroup):
    waiting_hours = State()

class RemoveDeadline(StatesGroup):
    waiting_hours = State()

class SendMessage(StatesGroup):
    waiting_message = State()

class EnterName(StatesGroup):
    waiting_name = State()