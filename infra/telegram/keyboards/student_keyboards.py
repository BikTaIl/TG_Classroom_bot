from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Any

def get_student_menu() -> InlineKeyboardMarkup:
    """Основная клавиатура студента"""
    buttons = [
        [InlineKeyboardButton(text="Установить/сбросить активный курс", callback_data="set_student_active_course")],
        [InlineKeyboardButton(text="Установить/сбросить активное задание", callback_data="set_student_active_assignment")],
        [InlineKeyboardButton(text="Получить список уведомлений", callback_data="get_student_notification_rules")],
        [InlineKeyboardButton(text="Добавить правило уведомлений", callback_data="add_student_notification_rule")],
        [InlineKeyboardButton(text="Удалить правило уведомлений", callback_data="remove_student_notification_rule")],
        [InlineKeyboardButton(text="Сбросить правила уведомлений к дефолтным", callback_data="reset_student_notification_rules_to_default")],
        [InlineKeyboardButton(text="Сводка всех активных заданий", callback_data="get_student_active_assignments_summary")],
        [InlineKeyboardButton(text="Сводка всех просроченных заданий", callback_data="get_student_overdue_assignments_summary")],
        [InlineKeyboardButton(text="Сводка по всем оцененным заданиям", callback_data="get_student_grades_summary")],
        [InlineKeyboardButton(text="Подробности по конкретной задаче", callback_data="get_student_assignment_details")],
        [InlineKeyboardButton(text="Отправить обратную связь по курсу", callback_data="submit_course_feedback")],
        [InlineKeyboardButton(text="В главное меню", callback_data="start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def return_to_the_menu() -> InlineKeyboardMarkup:
    """Клавиатура, появляющаяся после успешного запроса/
    успешного выполнения функции и отправляющая в стартовое
    меню или в меню студента"""
    buttons = [
        [InlineKeyboardButton(text="В меню студента", callback_data="start_student")],
        [InlineKeyboardButton(text="В главное меню", callback_data="start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def is_anonymus() -> InlineKeyboardMarkup:
    """Выбор анонимности/неанонимности обратной связи учителю"""
    buttons = [
        [InlineKeyboardButton(text="Да", callback_data="is_anonymus"),
         InlineKeyboardButton(text="Нет", callback_data="is_not_anonymus")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def have_to_choose_course() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Установить активный курс", callback_data="choose_teacher_active_course")],
        [InlineKeyboardButton(text="В меню студента", callback_data="start_student")],
        [InlineKeyboardButton(text="В главное меню", callback_data="start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def choose_course(courses: list[tuple[Any, ...]], page: int) -> InlineKeyboardMarkup:
    courses.append((0, "Сбросить курс"))
    pages = (len(courses) + 5) // 6
    buttons = [[InlineKeyboardButton(text=courses[i][1], callback_data=f"set_student_active_course:{str(courses[i][0])}")] for i in range(page * 6, min((page + 1) * 6, len(courses)))]
    if page > 0:
        buttons.append(
            [InlineKeyboardButton(text="Предыдущая страница",
                                 callback_data=f"previous_paper_course_student:{str(page)}")]
        )
    if page < pages - 1:
        buttons.append(
            [InlineKeyboardButton(text="Следующая страница", callback_data=f"next_paper_course_student:{str(page)}" )]
        )
    buttons.append([InlineKeyboardButton(text="В меню студента", callback_data="start_student")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def choose_assignment(assignments: list[tuple[Any, ...]], page: int) -> InlineKeyboardMarkup:
    assignments.append((0, "Сбросить задание"))
    pages = (len(assignments) + 5) // 6
    buttons = [[InlineKeyboardButton(text=assignments[i][1], callback_data=f"set_student_active_assignment:{str(assignments[i][0])}")] for i in range(page * 6, min((page + 1) * 6, len(assignments)))]
    if page > 0:
        buttons.append(
            [InlineKeyboardButton(text="Предыдущая страница",
                                  callback_data=f"previous_paper_assignment_student:{str(page)}")]
        )
    if page < pages - 1:
        buttons.append(
            [InlineKeyboardButton(text="Следующая страница", callback_data=f"next_paper_assignment_student:{str(page)}")]
        )
    buttons.append([InlineKeyboardButton(text="В меню студента", callback_data="start_student")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
