from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text, func
from models.gh_client import GitHubClassroomClient
from models.db import Submission, GithubAccount, Assignment, Course, User, Notification
from typing import Optional
from datetime import datetime

gh = GitHubClassroomClient()


async def sync_function(session: AsyncSession) -> None:
    """Функция для перезаполнения БД
    :param session: AsyncSession
    :returns None"""
    courses = await gh.get_courses()
    all_courses: list[Course] = []
    all_assignments: list[Assignment] = []
    all_submissions: list[Submission] = []
    try:
        async with session.begin():
            for course in courses:
                details: dict = await gh.get_course_details(course['id'])
                course_id: int = course['id']
                course_name: str = course['name']
                course_organization_name: str = details['organization']['login']
                new_course: Course = Course(
                    classroom_id=course_id,
                    name=course_name,
                    organization_name=course_organization_name
                )
                all_courses.append(new_course)
                session.add(new_course)
                assignments = await gh.get_assignments(course["id"])
                for assignment in assignments:
                    assignment_id: int = assignment['id']
                    title: str = assignment['title']
                    deadline_full: datetime = datetime.strptime(assignment['deadline'], '%Y-%m-%dT%H:%M:%SZ')
                    new_assignment: Assignment = Assignment(
                        classroom_id=course_id,
                        github_assignment_id=assignment_id,
                        title=title,
                        deadline_full=deadline_full
                    )
                    all_assignments.append(new_assignment)
                    session.add(new_assignment)
                    submissions = await gh.get_submissions(assignment["id"])
                    for submission in submissions:
                        submission_id: int = submission['id']
                        github_username: str = submission['students'][0]['login']
                        result_tg_id = await session.execute(
                            select(GithubAccount.user_telegram_id).filter(
                                GithubAccount.github_username == github_username)
                        )
                        student_telegram_id: Optional[int] = result_tg_id.scalar_one_or_none()
                        repo_url: str = submission['repository']['html_url']
                        is_submitted: bool = submission['submitted']
                        score: Optional[float] = submission['grade']
                        new_submission: Submission = Submission(
                            submission_id=submission_id,
                            assignment_id=assignment_id,
                            student_github_username=github_username,
                            student_telegram_id=student_telegram_id,
                            repo_url=repo_url,
                            is_submitted=is_submitted,
                            score=score
                        )
                        all_submissions.append(new_submission)
            await session.execute(text("DELETE FROM courses"))
            await session.execute(text("DELETE FROM assignments"))
            await session.execute(text("DELETE FROM submissions"))
            for course in all_courses:
                session.add(course)
            for assignment in all_assignments:
                session.add(assignment)
            for submission in all_submissions:
                session.add(submission)
    except Exception as e:
        raise e


async def get_students_nearing_deadline(session: AsyncSession) -> set[tuple[int, str, str]]:
    """
    Вытащить (telegram_id, course_name, assignment_title)
    для студентов, у которых желаемое время уведомления
    попадает в окно [NOW(), NOW() + 20 мин]
    Используется в scheduler
    :param session: AsyncSession
    :returns tuple(tg_id, course_name, assignment_name)
    """
    now = func.now()
    twenty_minutes_later = now + text("INTERVAL '20 minutes'")
    notification_trigger_time = (
            Assignment.deadline_full -
            (Notification.notification_time * text("INTERVAL '1 hour'"))
    )
    query = (
        select(
            User.telegram_id.label("telegram_id"),
            Course.name.label("course_name"),
            Assignment.title.label("assignment_name")
        )
        .join(Notification, User.telegram_id == Notification.telegram_id)
        .join(Submission, User.telegram_id == Submission.student_telegram_id)
        .join(Assignment, Submission.assignment_id == Assignment.github_assignment_id)
        .join(Course, Assignment.classroom_id == Course.classroom_id)
        .where(
            notification_trigger_time.between(
                now,
                twenty_minutes_later
            ),
            User.notifications_enabled is True
        )
        .distinct()
    )
    result = await session.execute(query)
    notificated_students = {
        (row.telegram_id, row.course_name, row.assignment_name)
        for row in result
    }
    return notificated_students
