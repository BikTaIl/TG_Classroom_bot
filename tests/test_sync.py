import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models.db import Base, User, Course, Assignment, Submission, Notification, OAuthState, GitOrganization
from commands.sync import (
    sync_function,
    get_students_nearing_deadline,
    delete_overdued_states,
    zero_sync_counter
)
from unittest.mock import AsyncMock, patch

DATABASE_URL = "postgresql+asyncpg://bot_admin@localhost:5433/testdb"

@pytest_asyncio.fixture(scope="function")
async def async_session():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session_maker() as session:
        student = User(telegram_id=1, telegram_username="student1", active_github_username="stud_github",
                       notifications_enabled=True, sync_count=5)
        teacher = User(telegram_id=2, telegram_username="teacher1", active_github_username="teacher_git",
                       notifications_enabled=True, sync_count=4)
        organization = GitOrganization(organization_name="Org1", teacher_telegram_id=2)
        course = Course(classroom_id=101, name="Course 101", organization_name="Org1")
        assignment1 = Assignment(
            github_assignment_id=201,
            classroom_id=101,
            title="Assignment 1",
            max_score=100,
            deadline_full=datetime.now() + timedelta(hours=1)
        )
        assignment2 = Assignment(
            github_assignment_id=202,
            classroom_id=101,
            title="Assignment 2",
            max_score=50,
            deadline_full=datetime.now() - timedelta(days=1)
        )
        submission1 = Submission(
            id=301,
            assignment_id=201,
            student_github_username="stud_github",
            student_telegram_id=1,
            is_submitted=True,
            score=90,
            submitted_at=datetime.now()
        )
        notification1 = Notification(telegram_id=1, notification_time=1)
        oauth_state = OAuthState(state="old", created_at=datetime.now() - timedelta(minutes=30), telegram_id=1)
        session.add_all([student, teacher])
        await session.commit()
        session.add(organization)
        await session.commit()
        session.add(course)
        await session.commit()
        session.add_all([assignment1, assignment2, submission1, notification1, oauth_state])
        await session.commit()
        yield session
    await engine.dispose()

@pytest.mark.asyncio
async def test_get_students_nearing_deadline(async_session):
    result = await get_students_nearing_deadline(async_session)
    assert isinstance(result, set)
    for entry in result:
        assert len(entry) == 4

@pytest.mark.asyncio
async def test_delete_overdued_states(async_session):
    await delete_overdued_states(async_session)
    res = await async_session.execute(select(OAuthState).where(OAuthState.state == "old"))
    assert res.scalar_one_or_none() is None

@pytest.mark.asyncio
async def test_zero_sync_counter(async_session):
    with patch("commands.sync.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2025, 12, 22, 0, 10)
        await zero_sync_counter(async_session)
    student = await async_session.get(User, 1)
    assert student.sync_count == 0

@pytest.mark.asyncio
async def test_sync_function(async_session):
    mock_courses = [{"id": 101, "name": "Course 101"}]
    mock_course_details = {"organization": {"login": "Org1"}}
    mock_assignments = [{"id": 201, "title": "Assignment 1", "deadline": "2025-12-30T12:00:00Z"}]
    mock_submissions = [{
        "id": 301,
        "students": [{"login": "stud_github"}],
        "repository": {"html_url": "https://github.com/test/repo"},
        "submitted": True,
        "last_commit_at": "2025-12-21T10:00:00Z",
        "grade": 95
    }]
    with patch("commands.sync.gh.get_courses", new_callable=AsyncMock) as mock_get_courses, \
         patch("commands.sync.gh.get_course_details", new_callable=AsyncMock) as mock_get_course_details, \
         patch("commands.sync.gh.get_assignments", new_callable=AsyncMock) as mock_get_assignments, \
         patch("commands.sync.gh.get_submissions", new_callable=AsyncMock) as mock_get_submissions:
        mock_get_courses.return_value = mock_courses
        mock_get_course_details.return_value = mock_course_details
        mock_get_assignments.return_value = mock_assignments
        mock_get_submissions.return_value = mock_submissions
        await sync_function(async_session)
    courses = await async_session.execute(select(Course).where(Course.classroom_id == 101))
    assert courses.scalar_one_or_none() is not None
    assignments = await async_session.execute(select(Assignment).where(Assignment.github_assignment_id == 201))
    assert assignments.scalar_one_or_none() is not None
    submissions = await async_session.execute(select(Submission).where(Submission.id == 301))
    assert submissions.scalar_one_or_none() is not None
