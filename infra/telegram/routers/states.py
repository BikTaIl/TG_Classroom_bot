from aiogram.fsm.state import State, StatesGroup


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