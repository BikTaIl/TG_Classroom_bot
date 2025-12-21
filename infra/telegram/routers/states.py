from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm.base import state_class_str

"""Список всех состояний для всех функций, требющих отдельного ввода 
(функции учителя и ассистента частично дублируются, так что к некоторым 
в конце добавлено Teacher или Assistant, чтобы ассистент случайно не перешел
в функцию учителя, тем самым случайно получив права учителя"""

class AddTeacher(StatesGroup):
    waiting_username = State()

class AddAssistant(StatesGroup):
    waiting_username = State()

class RemoveTeacher(StatesGroup):
    waiting_username = State()

class RemoveAssistant(StatesGroup):
    waiting_username = State()

class Ban(StatesGroup):
    waiting_username = State()

class Unban(StatesGroup):
    waiting_username = State()

class FindErrors(StatesGroup):
    waiting_date = State()

class ChangeRole(StatesGroup):
    waiting_role = State()

class ChangeGitHubAccount(StatesGroup):
    waiting_login = State()

class ChangeCourseTeacher(StatesGroup):
    waiting_course_id = State()

class ChangeCourseAssistant(StatesGroup):
    waiting_course_id = State()

class ChangeAssignmentTeacher(StatesGroup):
    waiting_course_id = State()

class ChangeAssignmentAssistant(StatesGroup):
    waiting_course_id = State()

class NewDeadline(StatesGroup):
    waiting_hours = State()

class RemoveDeadline(StatesGroup):
    waiting_hours = State()

class SendMessage(StatesGroup):
    waiting_message = State()

class EnterName(StatesGroup):
    waiting_name = State()

class AddOrganisation(StatesGroup):
    waiting_name = State()