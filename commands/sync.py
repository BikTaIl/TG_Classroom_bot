from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from models.gh_client import GitHubClassroomClient
from models.db import Submission, GithubAccount, ErrorLog, Assignment, Course
from typing import Optional
from datetime import datetime

gh = GitHubClassroomClient()


async def sync_function(session: AsyncSession) -> None:
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
