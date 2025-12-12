from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Sequence, Mapping, Any
from datetime import datetime


async def set_student_active_course(telegram_id: int, course_id: Optional[int], session: AsyncSession) -> None:
    """Установить/или сбросить активный курс студента."""


async def get_student_notification_rules(telegram_id: int, session: AsyncSession) -> Sequence[int]:
    """Получить список времен уведомлений студента."""


async def add_student_notification_rule(telegram_id: int, hours_before: int, session: AsyncSession) -> None:
    """Добавить новое правило уведомлений."""


async def remove_student_notification_rule(telegram_id: int, hours_before: int, session: AsyncSession) -> None:
    """Удалить правило уведомлений."""


async def reset_student_notification_rules_to_default(telegram_id: int, session: AsyncSession) -> None:
    """Сбросить правила уведомлений к дефолтным."""


async def get_student_active_assignments_summary(
        telegram_id: int, session: AsyncSession,
        course_id: Optional[int] = None
) -> Sequence[Mapping[str, Any]]:
    """Сводка всех активных заданий студента. Сортировка по дд"""


async def get_student_overdue_assignments_summary(
        telegram_id: int,
        session: AsyncSession,
        course_id: Optional[int] = None,
        now: Optional[datetime] = None
) -> Sequence[Mapping[str, Any]]:
    """Сводка всех просроченных заданий студента. Сортировка по дд"""


async def get_student_grades_summary(
        telegram_id: int,
        session: AsyncSession,
        course_id: Optional[int] = None
) -> Sequence[Mapping[str, Any]]:
    """Сводка по оценкам за сданные задачи — оценено/не оценено + баллы. Сортировка по дд"""


async def get_student_assignment_details(
        telegram_id: int,
        assignment_id: int,
        session: AsyncSession
) -> Mapping[str, Any]:
    """Подробности по конкретной задаче: статус, балл, дата сдачи."""


async def submit_course_feedback(
        telegram_id: int,
        course_id: int,
        message: str,
        anonymous: bool,
        session: AsyncSession
) -> None:
    """Отправить анонимную или неанонимную обратную связь по курсу."""