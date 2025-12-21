from typing import Optional, Sequence, Mapping, Any
from datetime import datetime, date
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from decimal import Decimal

from models.db import User, GithubAccount, Notification, Course, Assignment, Assistant, Submission, Permission, \
    ErrorLog, AccessDenied, GitOrganization


async def _get_students_courses(telegram_id: int, session: AsyncSession) -> Sequence[int]:
    """Все курсы студента из Submitted"""
    query = select(Assignment.classroom_id).distinct().join(
        Submission, Submission.assignment_id == Assignment.github_assignment_id
    ).where(
        Submission.student_telegram_id == telegram_id
    )
    result = await session.execute(query)
    return result.scalars().all()


async def get_student_notification_rules(telegram_id: int, session: AsyncSession) -> Sequence[int]:
    """Получить список времен уведомлений студента."""
    stmt = select(Notification.notification_time).where(Notification.telegram_id == telegram_id)
    stmt = stmt.order_by(Notification.notification_time.desc())
    result = await session.execute(stmt)
    return [row[0] for row in result.all()]


async def add_student_notification_rule(telegram_id: int, hours_before: int, session: AsyncSession) -> None:
    """Добавить новое правило уведомлений."""
    user = await session.get(User, telegram_id)
    if not user:
        raise ValueError("Пользователь не найден")
    existing = await session.get(Notification, (telegram_id, hours_before))
    if existing:
        raise ValueError("Правило уже существует")

    notification = Notification(telegram_id=telegram_id, notification_time=hours_before)
    session.add(notification)
    await session.commit()


async def remove_student_notification_rule(telegram_id: int, hours_before: int, session: AsyncSession) -> None:
    """Удалить правило уведомлений."""
    stmt = delete(Notification).where(
        and_(
            Notification.telegram_id == telegram_id,
            Notification.notification_time == hours_before
        )
    )
    await session.execute(stmt)
    await session.commit()


async def reset_student_notification_rules_to_default(telegram_id: int, session: AsyncSession) -> None:
    """Сбросить правила уведомлений к дефолтным."""
    stmt = delete(Notification).where(Notification.telegram_id == telegram_id)
    await session.execute(stmt)
    defaults = [24, 3]
    for hours in defaults:
        notification = Notification(telegram_id=telegram_id, notification_time=hours)
        session.add(notification)

    await session.commit()


async def get_student_active_assignments_summary(
        telegram_id: int,
        course_id: Optional[int] = None,
        session: AsyncSession = None
) -> Sequence[Mapping[str, Any]]:
    """Сводка всех активных заданий студента. Сортировка по дд"""
    courses = await _get_students_courses(telegram_id, session)
    if course_id:
        if course_id not in courses:
            raise ValueError("Студент не принадлежит курсу.")
        else:
            courses = [course_id]
    current_time = datetime.now()
    query = select(
        Course.name.label("course_name"),
        Assignment.title.label("assignment_title"),
        Assignment.deadline_full.label("deadline")
    ).join(
        Assignment, Course.classroom_id == Assignment.classroom_id
    ).where(
        and_(
            Course.classroom_id.in_(courses),
            Assignment.deadline_full > current_time
        )
    ).order_by(
        Assignment.deadline_full
    )
    assignments = await session.execute(query)
    return [
        {"course_name": a.course_name,
         "assignment_title": a.assignment_title,
         "deadline": a.deadline}
        for a in assignments.all()
    ]


async def get_student_overdue_assignments_summary(
        telegram_id: int,
        course_id: Optional[int] = None,
        now: Optional[datetime] = None,
        session: AsyncSession = None
) -> Sequence[Mapping[str, Any]]:
    """Сводка всех просроченных заданий студента. Сортировка по дд"""
    courses = await _get_students_courses(telegram_id, session)
    if course_id:
        if course_id not in courses:
            raise ValueError("Студент не принадлежит курсу.")
        else:
            courses = [course_id]
    if not now:
        now = datetime.now()
    query = select(
        Course.name.label("course_name"),
        Assignment.title.label("assignment_title"),
        Assignment.deadline_full.label("deadline")
    ).join(
        Assignment, Course.classroom_id == Assignment.classroom_id
    ).join(
        Submission,
        (Assignment.github_assignment_id == Submission.assignment_id) &
        (Submission.student_telegram_id == telegram_id)
    ).where(
        and_(
            Course.classroom_id.in_(courses),
            Assignment.deadline_full <= now,
            or_(
                Submission.is_submitted == False,
                Submission.is_submitted.is_(None)
            )
        )
    ).order_by(
        Assignment.deadline_full
    )
    assignments = await session.execute(query)
    return [
        {"course_name": a.course_name,
         "assignment_title": a.assignment_title,
         "deadline": a.deadline}
        for a in assignments.all()
    ]


async def get_student_grades_summary(
        telegram_id: int,
        course_id: Optional[int] = None,
        session: AsyncSession = None
) -> Sequence[Mapping[str, Any]]:
    """
    Сводка по оценкам за сданные задачи — оценено/не оценено + баллы.
    """
    courses = await _get_students_courses(telegram_id, session)
    if course_id:
        if course_id not in courses:
            raise ValueError("Студент не принадлежит курсу.")
        else:
            courses = [course_id]
    query = select(
        Course.name.label("course_name"),
        Assignment.title.label("assignment_title"),
        Assignment.deadline_full.label("deadline"),
        Submission.score.label("score"),
        Assignment.max_score.label("max_score"),
        Submission.submitted_at.label("submitted_at")  # Добавим для информации
    ).join(
        Assignment, Course.classroom_id == Assignment.classroom_id
    ).join(
        Submission,
        and_(
            Submission.assignment_id == Assignment.github_assignment_id,
            Submission.student_telegram_id == telegram_id,
            Submission.is_submitted is True
        )
    ).where(
        Assignment.classroom_id.in_(courses)
    )

    query = query.order_by(Assignment.deadline_full)

    result = await session.execute(query)
    rows = result.mappings().all()

    summary = []
    for row in rows:
        status = "оценено" if row["score"] is not None else "не оценено"
        summary.append({
            "course": row["course_name"],
            "assignment": row["assignment_title"],
            "deadline": row["deadline"],
            "submitted_at": row["submitted_at"],
            "status": status,
            "score": float(row["score"]) if row["score"] is not None else None,
            "max_score": float(row["max_score"]) if row["max_score"] is not None else None
        })

    return summary


async def get_student_assignment_details(
        telegram_id: int,
        assignment_id: int,
        session: AsyncSession = None
) -> Mapping[str, Any]:
    """Подробности по конкретной задаче: статус, балл, дата сдачи."""
    courses = await _get_students_courses(telegram_id, session)
    course = await select(Assignment.classroom_id).where(Assignment.github_assignment_id == assignment_id).one_or_none()
    if course not in courses:
        raise ValueError("Студент не может просматривать данное задание.")
    query = select(
        Assignment.title,
        Assignment.deadline_full,
        Submission.score,
        Submission.submitted_at,
        Course.name,
        Submission.is_submitted
    ).join(
        Course, Assignment.classroom_id == Course.classroom_id
    ).join(
        Submission,
        and_(
            Submission.assignment_id == Assignment.github_assignment_id,
            Submission.student_telegram_id == telegram_id
        ),
        isouter=True
    ).where(
        Assignment.github_assignment_id == assignment_id
    )

    result = await session.execute(query)
    row = result.first()

    if not row:
        return {}
    status = "не сдано"
    if row.is_submitted:
        status = "сдано" if row.score is not None else "ожидает оценки"

    return {
        "assignment": row.title,
        "course": row.name,
        "deadline": row.deadline_full,
        "status": status,
        "score": float(row.score) if row.score else None,
        "submitted_at": row.submitted_at
    }


async def submit_course_feedback(
        telegram_id: int,
        course_id: int,
        message: str,
        anonymous: bool,
        session: AsyncSession = None
) -> int:
    """Отправить анонимную или неанонимную обратную связь по курсу."""
    course_query = select(GitOrganization.teacher_telegram_id).where(
        (GitOrganization.course == course_id)
    )
    course = await session.execute(course_query)
    if not course.scalar_one():
        raise ValueError(f"Курса {course_id} не существует.")
    return course.scalar_one()
