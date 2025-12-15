from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_student_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Установить/сбросить активный курс", callback_data="set_student_active_course")],
        [InlineKeyboardButton(text="Получить список уведомлений", callback_data="get_student_notification_rules")],
        [InlineKeyboardButton(text="Добавить правило уведомлений", callback_data="add_student_notification_rule")],
        [InlineKeyboardButton(text="Удалить правило уведомлений", callback_data="remove_student_notification_rule")],
        [InlineKeyboardButton(text="Сбросить правила уведомлений к дефолтным", callback_data="reset_student_notification_rules_to_default")],
        [InlineKeyboardButton(text="Сводка всех активных заданий", callback_data="get_student_active_assignments_summary")],
        [InlineKeyboardButton(text="Сводка всех просроченных заданий", callback_data="get_student_overdue_assignments_summary")],
        [InlineKeyboardButton(text="Сводка по всем оцененным заданиям", callback_data="get_student_grades_summary")],
        [InlineKeyboardButton(text="Подробности по конкретной задаче", callback_data="get_student_assignment_details")],
        [InlineKeyboardButton(text="Отправить обратную связь по курсу", callback_data="submit_course_feedback")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def return_to_the_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="В меню студента", callback_data="start_student")],
        [InlineKeyboardButton(text="В главное меню", callback_data="start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def is_anonymus() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Да", callback_data="is_anonymus"),
         InlineKeyboardButton(text="Нет", callback_data="is_not_anonymus")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
