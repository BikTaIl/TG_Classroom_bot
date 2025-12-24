from typing import Optional, Sequence, Mapping, Any
from datetime import datetime
from sqlalchemy import select, delete, and_, or_, func, case, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from models.db import User, GithubAccount, Course, Assignment, Assistant, Submission, Permission, AccessDenied, \
    GitOrganization


async def _get_user_by_username(username: str, session: AsyncSession) -> Optional[User]:
    """Найти пользователя по username"""
    if username[0] == '@':
        username = username[1:]
    stmt = select(User).where(User.telegram_username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def _check_permission(telegram_id: int, key_roles: list[str], course_id: int, session: AsyncSession) -> None:
    """Проверить, имеет ли пользователь активную роль"""
    user = await session.get(User, telegram_id)
    if user is None:
        raise ValueError(f"Такого пользователя не существует")
    if user.banned:
        raise AccessDenied(f"Пользователь {telegram_id} забанен.")
    role = user.active_role
    if role not in key_roles:
        raise AccessDenied(f"Роль недоступна.")
    if role == 'teacher' and 'teacher' in key_roles:
        teacher_query = await session.execute(select(GitOrganization.organization_name).where(
            (GitOrganization.teacher_telegram_id == telegram_id))
        )
        teacher = teacher_query.scalar_one_or_none()
        course_query = await session.execute(select(Course).where(Course.organization_name == teacher))
        if teacher is None or course_query is None:
            raise ValueError(f"Недостаточно прав.")
    elif role == 'assistant' and 'assistant' in key_roles:
        assistant_query = select(Assistant).where(Assistant.course_id == course_id,
                                                  Assistant.telegram_id == telegram_id)
        assistant = await session.execute(assistant_query)
        if not assistant:
            raise ValueError("Недостаточно прав.")
    elif role == 'admin':
        return
    else:
        raise ValueError("Передана некорректная роль.")


async def get_course_students_overview(
        telegram_id: int,
        course_id: int,
        session: AsyncSession = None
) -> Sequence[Mapping[str, Any]]:
    """Сводка: ФИО, GitHub, дата последней отправки, средний балл, несданные задания."""
    await _check_permission(telegram_id, ['teacher', 'assistant', 'admin'], course_id, session)

    course_students_subq = select(
        distinct(Submission.student_telegram_id).label("student_telegram_id")
    ).join(
        Assignment, Assignment.github_assignment_id == Submission.assignment_id
    ).where(
        Assignment.classroom_id == course_id
    ).subquery()

    assignment_ids_result = await session.execute(
        select(Assignment.github_assignment_id).where(Assignment.classroom_id == course_id)
    )
    assignment_ids = assignment_ids_result.scalars().all()

    if not assignment_ids:
        return []

    students_query = select(
        User.telegram_id,
        User.full_name.label('full_name'),
        User.active_github_username.label('github_username'),
        func.max(Submission.submitted_at).label("last_submission_time"),
        func.avg(
            case(
                (Submission.score.is_not(None), Submission.score),
                else_=None
            )
        ).label("avg_score")
    ).select_from(User).join(
        course_students_subq,
        course_students_subq.c.student_telegram_id == User.telegram_id
    ).outerjoin(
        Submission,
        and_(
            Submission.student_telegram_id == User.telegram_id,
            Submission.assignment_id.in_(assignment_ids)
        )
    ).group_by(
        User.telegram_id, User.full_name, User.active_github_username
    ).order_by(User.full_name)

    students_result = await session.execute(students_query)
    students_data = students_result.mappings().all()

    if students_data:
        student_ids = [s['telegram_id'] for s in students_data]

        all_assignments_query = select(
            Assignment.github_assignment_id,
            Assignment.title
        ).where(Assignment.classroom_id == course_id)

        all_assignments_result = await session.execute(all_assignments_query)
        all_assignments = {a.github_assignment_id: a.title for a in all_assignments_result.all()}

        submitted_query = select(
            Submission.student_telegram_id,
            Submission.assignment_id
        ).where(
            and_(
                Submission.assignment_id.in_(assignment_ids),
                Submission.student_telegram_id.in_(student_ids),
                Submission.is_submitted == True
            )
        )

        submitted_result = await session.execute(submitted_query)
        submitted_map = {}

        for row in submitted_result.all():
            student_id = row.student_telegram_id
            assignment_id = row.assignment_id
            if student_id not in submitted_map:
                submitted_map[student_id] = set()
            submitted_map[student_id].add(assignment_id)
    overview = []

    for student in students_data:
        student_id = student['telegram_id']

        # Находим несданные задания
        not_submitted = []
        if student_id in submitted_map:
            submitted_assignments = submitted_map[student_id]
            for assignment_id, title in all_assignments.items():
                if assignment_id not in submitted_assignments:
                    not_submitted.append(title)
        else:
            not_submitted = list(all_assignments.values())

        overview.append({
            "full_name": student['full_name'],
            "github_username": student['github_username'],
            "last_submission_time": student['last_submission_time'],
            "avg_score": float(student['avg_score']) if student['avg_score'] is not None else None,
            "not_submitted_assignments": not_submitted,
            "not_submitted_count": len(not_submitted)
        })
    return overview


async def get_assignment_students_status(
        telegram_id: int,
        assignment_id: Optional[int] = None,
        session: AsyncSession = None
) -> Sequence[Mapping[str, Any]]:
    """Сводка по отдельному заданию: ФИО, GitHub, статус. Сортировка по статусу и ФИО"""
    if not assignment_id:
        return []
    course_query = select(Assignment.classroom_id).where(Assignment.github_assignment_id == assignment_id)
    course = await session.execute(course_query)
    await _check_permission(telegram_id, ['teacher', 'assistant', 'admin'], course.scalar_one(), session)

    ass_query = select(
        Assignment.title.label('title'),
        User.full_name.label('full_name'),
        User.active_github_username.label('github_username'),
        Submission.is_submitted.label('is_submitted'),
        Submission.score.label('score'),
    ).join(
        Submission, Submission.assignment_id == Assignment.github_assignment_id
    ).join(
        User, User.telegram_id == Submission.student_telegram_id
    ).where(
        Assignment.github_assignment_id == assignment_id
    ).order_by(User.full_name).order_by(Submission.is_submitted)
    result = await session.execute(ass_query)
    result_data = result.mappings().all()
    overview = []
    for row in result_data:
        status = "не сдано"
        if row.is_submitted:
            if row.score is not None:
                status = "оценено"
            else:
                status = "ожидает оценки"
        overview.append({
            "title": row.title,
            "full_name": row.full_name,
            "github_username": row.github_username,
            "status": status,
            "grade": row.score if row.score is not None else None
        })
    return overview


async def get_classroom_users_without_bot_accounts(
        telegram_id: int,
        course_id: Optional[int] = None,
        session: AsyncSession = None
) -> Sequence[str]:
    """GitHub-логины студентов, которых нет в боте."""
    await _check_permission(telegram_id, ['teacher', 'assistant', 'admin'], course_id, session)
    query = select(
        distinct(Submission.student_github_username)
    ).join(Assignment, Assignment.github_assignment_id == Submission.assignment_id).where(
        Submission.student_telegram_id == None, Assignment.classroom_id == course_id)
    result = await session.execute(query)
    return result.scalars().all()


async def get_course_deadlines_overview(
        telegram_id: int,
        course_id: Optional[int] = None,
        session: AsyncSession = None
) -> Sequence[Mapping[str, Any]]:
    """Сводка всех дедлайнов. Сортировка по дд"""
    org_query = await session.execute(
        select(GitOrganization.organization_name).where(GitOrganization.teacher_telegram_id == telegram_id))
    org = org_query.scalar_one_or_none()

    query = (select(
        Assignment.github_assignment_id,
        Assignment.title,
        Assignment.deadline_full,
        Course.name.label("course_name"),
        Course.classroom_id,
        func.count(distinct(GithubAccount.github_username)).label("total_students")
    ).join(
        Course, Assignment.classroom_id == Course.classroom_id
    ).join(
        Submission, Submission.assignment_id == Assignment.github_assignment_id
    ).outerjoin(
        GithubAccount, GithubAccount.github_username == Submission.student_github_username
    ).outerjoin(
        Assistant,
        and_(
            Assistant.course_id == Course.classroom_id,
            Assistant.telegram_id == telegram_id
        )
    ).where(
        or_(
            Course.organization_name == org,
            Assistant.telegram_id == telegram_id
        )
    ).group_by(
        Assignment.github_assignment_id,
        Assignment.title,
        Assignment.deadline_full,
        Course.name,
        Course.classroom_id
    ))

    if course_id:
        query = query.where(Course.classroom_id == course_id)

    result = await session.execute(query)
    assignments = result.mappings().all()

    if not assignments:
        return []

    assignment_ids = [a["github_assignment_id"] for a in assignments]

    submissions_query = select(
        Submission.assignment_id,
        func.count(Submission.id).label("submitted_count")
    ).where(
        and_(
            Submission.assignment_id.in_(assignment_ids),
            Submission.is_submitted == True
        )
    ).group_by(Submission.assignment_id)

    submissions_result = await session.execute(submissions_query)
    submissions_map = {row.assignment_id: row.submitted_count for row in submissions_result.all()}
    overview = []
    for assignment in assignments:
        submitted_count = submissions_map.get(Assignment.github_assignment_id, 0)
        total_students = assignment.total_students
        print(assignment)
        print(total_students)
        if total_students is None:
            total_students = 0
        print(total_students)
        overview.append({
            "assignment": assignment.title,
            "course": assignment.course_name,
            "deadline": assignment.deadline_full,
            "submitted_count": submitted_count,
            "not_submitted_count": total_students - submitted_count if total_students > 0 else 0
        })

    overview.sort(key=lambda x: x["deadline"] or datetime.max)

    return overview


async def get_tasks_to_grade_summary(
        telegram_id: int,
        course_id: Optional[int] = None,
        session: AsyncSession = None
) -> Sequence[Mapping[str, Any]]:
    """Сводка по задачам, которые нужно оценить. Сортировка по дд и названию курса"""
    org_query = await session.execute(
        select(GitOrganization.organization_name).where(GitOrganization.teacher_telegram_id == telegram_id))
    org = org_query.scalar_one_or_none()

    query = select(
        Assignment.title,
        Assignment.deadline_full,
        Course.name.label("course_name"),
        func.count(Submission.id).label("total_submissions"),
        func.count(case((Submission.score.is_not(None), 1))).label("graded_count")
    ).join(
        Course, Assignment.classroom_id == Course.classroom_id
    ).join(
        Submission, Submission.assignment_id == Assignment.github_assignment_id
    ).where(
        and_(
            Assignment.deadline_full < datetime.now(),
            or_(
                Course.organization_name == org,
                Assistant.telegram_id == telegram_id
            )
        )
    ).outerjoin(
        Assistant, Assistant.course_id == Course.classroom_id
    ).group_by(
        Assignment.title, Assignment.deadline_full, Course.name
    )

    if course_id:
        query = query.where(Course.classroom_id == course_id)

    query = query.order_by(Assignment.deadline_full, Course.name)

    result = await session.execute(query)
    rows = result.all()

    summary = []
    for row in rows:
        to_grade = row.total_submissions - row.graded_count
        summary.append({
            "assignment": row.title,
            "course": row.course_name,
            "deadline": row.deadline_full,
            "total_submissions": row.total_submissions,
            "graded_count": row.graded_count,
            "to_grade_count": to_grade
        })

    return summary


async def get_manual_check_submissions_summary(
        telegram_id: int,
        course_id: Optional[int] = None,
        session: AsyncSession = None
) -> Sequence[Mapping[str, Any]]:
    """Сводка по ручной проверке: ФИО, GitHub, даты сдачи и дедлайна."""
    org_query = await session.execute(
        select(GitOrganization.organization_name).where(GitOrganization.teacher_telegram_id == telegram_id))
    org = org_query.scalar_one_or_none()
    query = select(
        User.full_name,
        GithubAccount.github_username,
        Assignment.title,
        Assignment.deadline_full,
        Submission.submitted_at,
        Course.name.label("course_name")
    ).join(
        GithubAccount, User.telegram_id == GithubAccount.user_telegram_id
    ).join(
        Submission, Submission.student_telegram_id == User.telegram_id
    ).join(
        Assignment, Submission.assignment_id == Assignment.github_assignment_id
    ).join(
        Course, Assignment.classroom_id == Course.classroom_id
    ).where(
        and_(
            Assignment.grading_mode == "manual",
            or_(
                Course.organization_name == org,
                Assistant.telegram_id == telegram_id
            ),
            Submission.is_submitted == True,
            Submission.score.is_(None)
        )
    ).outerjoin(
        Assistant, Assistant.course_id == Course.classroom_id
    )

    if course_id:
        query = query.where(Course.classroom_id == course_id)

    query = query.order_by(Assignment.deadline_full, Course.name)

    result = await session.execute(query)
    rows = result.all()

    summary = []
    for row in rows:
        summary.append({
            "course": row.course_name,
            "assignment": row.title,
            "full_name": row.full_name,
            "github_username": row.github_username,
            "submitted_at": row.submitted_at,
            "deadline": row.deadline_full
        })

    return summary


async def get_teacher_deadline_notification_payload(
        teacher_telegram_id: int,
        assignment_id: int,
        session: AsyncSession = None
) -> Optional[Mapping[str, Any]]:
    """Данные для уведомления: сколько не сдали, список студентов, дедлайн."""

    assignment_query = select(
        Assignment,
        Course
    ).join(
        Course, Assignment.classroom_id == Course.classroom_id
    ).where(
        Assignment.github_assignment_id == assignment_id
    )

    result = await session.execute(assignment_query)
    row = result.first()

    if not row:
        return None

    assignment, course = row.Assignment, row.Course

    await _check_permission(teacher_telegram_id, ['teacher', 'admin'], course.classroom_id, session)
    students_in_course_query = select(
        distinct(Submission.student_telegram_id)
    ).join(
        Assignment, Submission.assignment_id == Assignment.github_assignment_id
    ).where(
        Assignment.classroom_id == course.classroom_id
    )

    students_result = await session.execute(students_in_course_query)
    student_telegram_ids = [row[0] for row in students_result.all()]

    if not student_telegram_ids:
        # Если нет студентов по сабмитам, пытаемся получить через GitHub аккаунты
        # (альтернативный подход, менее точный)
        students_query = select(User.telegram_id).distinct()
        students_result = await session.execute(students_query)
        student_telegram_ids = [row[0] for row in students_result.all()]
    not_submitted_students = []

    for student_id in student_telegram_ids:
        submission_query = select(Submission).where(
            and_(
                Submission.assignment_id == assignment_id,
                Submission.student_telegram_id == student_id,
                Submission.is_submitted == True
            )
        )

        submission_result = await session.execute(submission_query)
        submission = submission_result.scalar_one_or_none()
        if not submission:
            student_query = select(
                User.full_name,
                GithubAccount.github_username
            ).outerjoin(
                GithubAccount, User.telegram_id == GithubAccount.user_telegram_id
            ).where(
                User.telegram_id == student_id
            )

            student_result = await session.execute(student_query)
            student_row = student_result.first()

            if student_row:
                full_name, github_username = student_row
                not_submitted_students.append({
                    "full_name": full_name or "Неизвестно",
                    "github_username": github_username or "Нет GitHub"
                })

    return {
        "assignment": assignment.title,
        "course_name": course.name,
        "deadline": assignment.deadline_full,
        "not_submitted_count": len(not_submitted_students),
        "not_submitted_students": not_submitted_students,
        "assignment_id": assignment_id,
        "course_id": course.classroom_id
    }


async def add_course_assistant(
        teacher_telegram_id: int,
        course_id: int,
        assistant_telegram_username: str,
        session: AsyncSession = None
) -> None:
    """Добавить ассистента по username. Только для учителя"""
    if assistant_telegram_username[0] == '@':
        assistant_telegram_username = assistant_telegram_username[1:]
    await _check_permission(teacher_telegram_id, ['teacher', 'admin'], course_id, session)
    assistant = await _get_user_by_username(assistant_telegram_username, session)
    if not assistant:
        raise ValueError(f"Пользователь {assistant_telegram_username} не найден")
    org_query = await session.execute(
        select(GitOrganization.organization_name).where(GitOrganization.teacher_telegram_id == teacher_telegram_id))
    org = org_query.scalar_one_or_none()
    course_stmt = select(Course).where(
        and_(
            Course.classroom_id == course_id,
            Course.organization_name == org
        )
    )
    course_result = await session.execute(course_stmt)
    course = course_result.scalar_one_or_none()
    if not course:
        raise AccessDenied("Курс не найден или вы не являетесь его владельцем.")

    if assistant.telegram_id == teacher_telegram_id:
        raise ValueError("Учитель курса не может быть добавлен как ассистент.")

    existing_assistant_stmt = select(Assistant).where(
        and_(
            Assistant.telegram_id == assistant.telegram_id,
            Assistant.course_id == course_id
        )
    )
    existing_result = await session.execute(existing_assistant_stmt)
    existing_assistant = existing_result.scalar_one_or_none()

    if existing_assistant:
        raise ValueError("Ассистент уже добавлен в этот курс")

    new_assistant = Assistant(
        telegram_id=assistant.telegram_id,
        course_id=course_id
    )
    permission_find_query = await session.execute(select(Permission).where(
        Permission.telegram_id == assistant.telegram_id,
        Permission.permitted_role == 'assistant'
    ))
    permission_find = permission_find_query.scalar_one_or_none()
    if permission_find is None:
        permission = Permission(
            telegram_id=new_assistant.telegram_id,
            permitted_role='assistant'
        )
        session.add(permission)
    session.add(new_assistant)
    await session.commit()


async def remove_course_assistant(
        teacher_telegram_id: int,
        course_id: int,
        assistant_telegram_username: str,
        session: AsyncSession = None
) -> None:
    """Удалить ассистента. Только для учителя"""
    if assistant_telegram_username[0] == '@':
        assistant_telegram_username = assistant_telegram_username[1:]
    await _check_permission(teacher_telegram_id, ['teacher', 'admin'], course_id, session)
    assistant = await _get_user_by_username(assistant_telegram_username, session)
    if not assistant:
        raise ValueError(f"Пользователь {assistant_telegram_username} не найден")
    org_query = await session.execute(
        select(GitOrganization.organization_name).where(GitOrganization.teacher_telegram_id == teacher_telegram_id))
    org = org_query.scalar_one_or_none()
    course_stmt = select(Course).where(
        and_(
            Course.classroom_id == course_id,
            Course.organization_name == org
        )
    )
    course_result = await session.execute(course_stmt)
    course = course_result.scalar_one_or_none()
    if not course:
        raise AccessDenied("Курс не найден или вы не являетесь его владельцем.")

    existing_assistant_stmt = select(Assistant).where(
        and_(
            Assistant.telegram_id == assistant.telegram_id,
            Assistant.course_id == course_id
        )
    )
    existing_result = await session.execute(existing_assistant_stmt)
    existing_assistant = existing_result.scalar_one_or_none()

    if not existing_assistant:
        raise ValueError("Ассистент уже добавлен в этот курс")

    stmt = delete(Assistant).where(Assistant.telegram_id == assistant.telegram_id)
    await session.execute(stmt)
    await session.commit()


async def create_course_announcement(
        teacher_telegram_id: int,
        course_id: int,
        session: AsyncSession = None
) -> Sequence[int]:
    """Возвращает список студентов, которым надо разослать объявления"""
    await _check_permission(teacher_telegram_id, ['teacher', 'admin'], course_id, session)
    assignment_stmt = select(Assignment.github_assignment_id).where(Assignment.classroom_id == course_id)
    assignment_result = await session.execute(assignment_stmt)
    query = select(Submission.student_telegram_id).where(
        Submission.assignment_id.in_(assignment_result.scalars().all()),
        Submission.student_telegram_id.isnot(None)
    )
    submission_result = await session.execute(query)
    return submission_result.scalars().all()


async def trigger_manual_sync_for_teacher(
        teacher_telegram_id: int,
        session: AsyncSession = None
) -> bool:
    """Выполнить ручную синхронизацию данных по курсу. Только для учителя"""
    user = await session.get(User, teacher_telegram_id)
    if not user:
        raise ValueError(f"Пользователя {teacher_telegram_id} не существует.")
    if user.sync_count is None or user.sync_count < 0:
        raise ValueError(f"У {teacher_telegram_id} некорректное поле sync_count.")
    if user.sync_count >= 3:
        try:
            await _check_permission(teacher_telegram_id, ['admin', 'teacher'], 0, session)
        except AccessDenied:
            raise ValueError(f"Вы сделали больше 3 обновлений")
    user.sync_count += 1
    await session.commit()
    return True


async def find_course(
        teacher_telegram_id: int,
        course_name: str,
        session: AsyncSession
) -> int:
    """Находит айди курса по айди учителя и названию курса"""
    org_query = await session.execute(
        select(GitOrganization.organization_name).where(GitOrganization.teacher_telegram_id == teacher_telegram_id))
    organization = org_query.scalar_one_or_none()
    if organization is None:
        raise ValueError('Учитель не привязан к организации')
    course_query = await session.execute(select(Course.classroom_id).where(
        Course.organization_name == organization,
        Course.name == course_name
    ))
    course = course_query.scalar_one_or_none()
    if course is None:
        raise ValueError('Курса с таким названием нет')
    return course


async def find_assignment(
        course_id: str,
        assignment_name: str,
        session: AsyncSession
) -> int:
    """Находит айди задания по айди курса и названию задания"""
    assignment_query = await session.execute(
        select(Assignment.github_assignment_id).where(
            Assignment.classroom_id == course_id,
            Assignment.title == assignment_name
        ))
    assignment_id = assignment_query.scalar_one_or_none()
    if assignment_id is None:
        raise ValueError('Задания с таким именем в данном курсе нет')
    return assignment_id


async def find_teachers_courses(
        teacher_telegram_id: int,
        session: AsyncSession
) -> list[tuple[Any, ...]]:
    """По айди учителя вытаскивает список курсов (айди и имена), которыми он владеет"""
    org_query = await session.execute(
        select(GitOrganization.organization_name).where(GitOrganization.teacher_telegram_id == teacher_telegram_id))
    organization = org_query.scalar_one_or_none()
    if organization is None:
        raise ValueError('Учитель не привязан к организации')
    course_query = await session.execute(select(Course.classroom_id, Course.name).where(
        Course.organization_name == organization
    ))
    return [tuple(row) for row in course_query.all()]


async def find_assistants_courses(
        assistant_telegram_id: int,
        session: AsyncSession
) -> list[tuple[Any, ...]]:
    """По айди ассистента вытаскивает список курсов (айди и имена), к которым он прикреплен"""
    courses_query = await session.execute(select(Assistant.course_id, Course.name
                                                 ).join(Course, Assistant.course_id == Course.classroom_id
                                                        ).where(Assistant.telegram_id == assistant_telegram_id))
    return [tuple(row) for row in courses_query.all()]


async def find_assignments_by_course_id(
        course_id: int,
        session: AsyncSession
) -> list[tuple[Any, ...]]:
    if course_id is None:
        raise ValueError('Курс не выбран')
    assignments_query = await session.execute(
        select(Assignment.github_assignment_id, Assignment.title).where(Assignment.classroom_id == course_id))
    return [tuple(row) for row in assignments_query.all()]


async def select_manual_check_assignment(
        assignment_id: int,
        session: AsyncSession
) -> None:
    if assignment_id is None:
        raise ValueError("Задание не выбрано")
    assignment = await session.get(Assignment, assignment_id)
    if assignment is None:
        raise ValueError("Выбранное задание отсутствует")
    assignment.grading_mode = 'manual'
    await session.commit()


async def delete_manual_check_assignment(
        assignment_id: int,
        session: AsyncSession
) -> None:
    if assignment_id is None:
        raise ValueError("Задание не выбрано")
    assignment = await session.get(Assignment, assignment_id)
    if assignment is None:
        raise ValueError("Выбранное задание отсутствует")
    assignment.grading_mode = 'auto'
    await session.commit()
