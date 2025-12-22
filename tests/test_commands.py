import pytest
import pytest_asyncio
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete
from models.db import (
    Base,
    User,
    Permission,
    ErrorLog,
    GitLogs,
    GitOrganization,
    AccessDenied,
    GithubAccount,
    Notification,
    Course,
    Assignment,
    Submission
)
from commands.common_commands import (
    create_user,
    set_active_role,
    toggle_global_notifications,
    change_git_account,
    enter_name
)
from commands.admin_commands import (
    grant_teacher_role,
    revoke_teacher_role,
    ban_user,
    unban_user,
    get_error_count_for_day,
    get_last_successful_github_call_time,
    get_last_failed_github_call_info,
    add_organisation
)
from commands.student_commands import (
    get_student_grades_summary,
    _get_students_courses,
    find_students_courses,
    get_student_overdue_assignments_summary,
    get_student_active_assignments_summary,
    reset_student_notification_rules_to_default,
    get_student_notification_rules,
    add_student_notification_rule,
    remove_student_notification_rule,
    get_student_assignment_details
)
from commands.teacher_and_assistant_commands import (
    _get_user_by_username,
    _check_permission,
    get_course_students_overview,
    get_assignment_students_status,
    get_classroom_users_without_bot_accounts,
    get_course_deadlines_overview,
    get_tasks_to_grade_summary
)

DATABASE_URL = "postgresql+asyncpg://molonovboris@localhost:5432/testdb"


@pytest_asyncio.fixture(scope="function")
async def async_session():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session_maker() as session:
        admin = User(telegram_id=6, telegram_username="admin_user", active_role='admin')
        target = User(telegram_id=7, telegram_username="target_user")
        permission = Permission(telegram_id=6, permitted_role='admin')
        student = User(
            telegram_id=8,
            telegram_username="student_user",
            active_github_username="stud_github",
            notifications_enabled=True
        )
        org = GitOrganization(organization_name="Org1", teacher_telegram_id=6)
        course = Course(classroom_id=101, name="Course 101", organization_name="Org1")
        assignment1 = Assignment(
            github_assignment_id=201,
            classroom_id=101,
            title="Assignment 1",
            max_score=100,
            deadline_full=datetime.now() + timedelta(days=1)
        )
        assignment2 = Assignment(
            github_assignment_id=202,
            classroom_id=101,
            title="Assignment 2",
            max_score=50,
            deadline_full=datetime.now() - timedelta(days=1)
        )
        submission1 = Submission(
            assignment_id=201,
            student_github_username="stud_github",
            student_telegram_id=8,
            is_submitted=True,
            score=90,
            submitted_at=datetime.now()
        )
        submission2 = Submission(
            assignment_id=202,
            student_github_username="stud_github",
            student_telegram_id=8,
            is_submitted=False
        )
        notification1 = Notification(telegram_id=8, notification_time=24)
        notification2 = Notification(telegram_id=8, notification_time=3)
        session.add_all([admin, target, student, permission])
        await session.flush()
        session.add(org)
        await session.flush()
        session.add(course)
        await session.flush()
        session.add_all([assignment1, assignment2])
        await session.flush()
        session.add_all([submission1, submission2, notification1, notification2])
        await session.commit()
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_user(async_session):
    await create_user(1, "testuser", async_session)
    result = await async_session.execute(select(User).where(User.telegram_id == 1))
    user = result.scalar_one()
    assert user.telegram_username == "testuser"
    assert user.active_role is None
    assert user.sync_count == 0
    assert user.notifications_enabled is True


@pytest.mark.asyncio
async def test_set_active_role(async_session):
    user = User(telegram_id=2, telegram_username="roleuser")
    permission = Permission(telegram_id=2, permitted_role="student")
    async_session.add_all([user, permission])
    await async_session.commit()

    await set_active_role(2, "student", async_session)
    updated_user = await async_session.get(User, 2)
    assert updated_user.active_role == "student"

    with pytest.raises(AccessDenied):
        await set_active_role(2, "teacher", async_session)

    with pytest.raises(ValueError):
        await set_active_role(2, "invalid_role", async_session)


@pytest.mark.asyncio
async def test_toggle_global_notifications(async_session):
    user = User(telegram_id=3, telegram_username="notifyuser", notifications_enabled=True)
    async_session.add(user)
    await async_session.commit()

    await toggle_global_notifications(3, async_session)
    updated_user = await async_session.get(User, 3)
    assert updated_user.notifications_enabled is False

    await toggle_global_notifications(3, async_session)
    updated_user = await async_session.get(User, 3)
    assert updated_user.notifications_enabled is True

    with pytest.raises(ValueError):
        await toggle_global_notifications(999, async_session)


@pytest.mark.asyncio
async def test_change_git_account(async_session):
    user = User(telegram_id=4, telegram_username="gituser")
    git = GithubAccount(github_username="gitlogin", user_telegram_id=4)
    async_session.add_all([user, git])
    await async_session.commit()

    await change_git_account(4, "gitlogin", async_session)
    updated_user = await async_session.get(User, 4)
    assert updated_user.active_github_username == "gitlogin"

    with pytest.raises(ValueError):
        await change_git_account(4, "wronglogin", async_session)


@pytest.mark.asyncio
async def test_enter_name(async_session):
    user = User(telegram_id=5, telegram_username="nameuser")
    async_session.add(user)
    await async_session.commit()

    await enter_name(5, "Full Name", async_session)
    updated_user = await async_session.get(User, 5)
    assert updated_user.full_name == "Full Name"


@pytest.mark.asyncio
async def test_grant_teacher_role_success(async_session):
    await grant_teacher_role(6, "target_user", async_session)
    res = await async_session.execute(select(Permission).where(Permission.telegram_id == 7))
    perms = res.scalars().all()
    assert any(p.permitted_role == 'teacher' for p in perms)


@pytest.mark.asyncio
async def test_grant_teacher_role_already_exists(async_session):
    await grant_teacher_role(6, "target_user", async_session)
    with pytest.raises(ValueError, match="уже имеет роль teacher"):
        await grant_teacher_role(6, "target_user", async_session)


@pytest.mark.asyncio
async def test_revoke_teacher_role(async_session):
    await grant_teacher_role(6, "target_user", async_session)
    await revoke_teacher_role(6, "target_user", async_session)
    stmt = select(Permission).where(Permission.telegram_id == 7,
                                    Permission.permitted_role == 'teacher')
    res = await async_session.execute(stmt)
    assert res.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_ban_unban_user(async_session):
    await ban_user(6, "target_user", async_session)
    user_stmt = select(User).where(User.telegram_id == 7)
    res = await async_session.execute(user_stmt)
    target = res.scalar_one()
    assert target.banned is True

    await unban_user(6, "target_user", async_session)
    res = await async_session.execute(user_stmt)
    target = res.scalar_one()
    assert target.banned is False


@pytest.mark.asyncio
async def test_get_error_count(async_session):
    error = ErrorLog(message="Test Error", created_at=datetime.now())
    async_session.add(error)
    await async_session.commit()
    today = date.today()
    count = await get_error_count_for_day(6, today, async_session)
    assert count == 1
    summary_len = await get_error_count_for_day(6, None, async_session)
    assert summary_len == 1


@pytest.mark.asyncio
async def test_github_logs_info(async_session):
    log_ok = GitLogs(log_status=200, log_message="OK", created_at=datetime.now() - timedelta(minutes=5))
    log_fail = GitLogs(log_status=404, log_message="Not Found", created_at=datetime.now())
    async_session.add_all([log_ok, log_fail])
    await async_session.commit()
    last_ok = await get_last_successful_github_call_time(6, async_session)
    assert last_ok is not None
    last_fail = await get_last_failed_github_call_info(6, async_session)
    assert last_fail["status"] == 404
    assert last_fail["message"] == "Not Found"


@pytest.mark.asyncio
async def test_add_organisation(async_session):
    await add_organisation(6, 7, "MyTestOrg", async_session)
    stmt = select(GitOrganization).where(GitOrganization.organization_name == "MyTestOrg")
    res = await async_session.execute(stmt)
    org = res.scalar_one_or_none()
    assert org is not None
    assert org.teacher_telegram_id == 7


@pytest.mark.asyncio
async def test_access_denied_for_non_admin(async_session):
    with pytest.raises(Exception):
        await ban_user(7, "admin_user", async_session)


@pytest.mark.asyncio
async def test_get_student_notification_rules(async_session):
    rules = await get_student_notification_rules(8, async_session)
    assert sorted(rules) == [3, 24]


@pytest.mark.asyncio
async def test_add_and_remove_student_notification_rule(async_session):
    await add_student_notification_rule(8, 5, async_session)
    rules = await get_student_notification_rules(8, async_session)
    assert 5 in rules

    with pytest.raises(ValueError):
        await add_student_notification_rule(8, 5, async_session)

    await remove_student_notification_rule(8, 5, async_session)
    rules = await get_student_notification_rules(8, async_session)
    assert 5 not in rules


@pytest.mark.asyncio
async def test_reset_student_notification_rules_to_default(async_session):
    await reset_student_notification_rules_to_default(8, async_session)
    rules = await get_student_notification_rules(8, async_session)
    assert sorted(rules) == [3, 24]


@pytest.mark.asyncio
async def test_get_student_active_assignments_summary(async_session):
    summary = await get_student_active_assignments_summary(8, session=async_session)
    assert any(a['assignment_title'] == "Assignment 1" for a in summary)
    assert all(a['deadline'] > datetime.now() for a in summary)


@pytest.mark.asyncio
async def test_get_student_overdue_assignments_summary(async_session):
    overdue = await get_student_overdue_assignments_summary(8, session=async_session)
    assert any(a['assignment_title'] == "Assignment 2" for a in overdue)


@pytest.mark.asyncio
async def test_get_student_grades_summary(async_session):
    grades = await get_student_grades_summary(8, session=async_session)
    assert any(a['assignment'] == "Assignment 1" and a['score'] == 90 for a in grades)


@pytest.mark.asyncio
async def test__get_students_courses(async_session):
    courses = await _get_students_courses(8, async_session)
    assert 101 in courses


@pytest.mark.asyncio
async def test_find_students_courses(async_session):
    courses = await find_students_courses(8, async_session)
    assert any(c[0] == 101 for c in courses)
    assert any(c[1] == "Course 101" for c in courses)

@pytest.mark.asyncio
async def test_get_student_courses_empty(async_session: AsyncSession):
    new_student = User(telegram_id=10, telegram_username="no_courses")
    async_session.add(new_student)
    await async_session.commit()

    courses = await _get_students_courses(10, session=async_session)
    assert courses == []

@pytest.mark.asyncio
async def test_get_student_grades_summary_multiple_courses(async_session: AsyncSession):
    org = await async_session.get(GitOrganization, "Org1")
    course2 = Course(classroom_id=102, name="Course 102", organization_name=org.organization_name)
    assignment3 = Assignment(
        github_assignment_id=203,
        classroom_id=102,
        title="Assignment 3",
        max_score=70,
        deadline_full=datetime.now() + timedelta(days=2)
    )
    submission3 = Submission(
        assignment_id=203,
        student_github_username="stud_github",
        student_telegram_id=8,
        is_submitted=True,
        score=65
    )
    async_session.add_all([course2, assignment3, submission3])
    await async_session.commit()

    grades = await get_student_grades_summary(8, session=async_session)
    titles = [g['assignment'] for g in grades]
    assert "Assignment 1" in titles
    assert "Assignment 3" in titles

@pytest.mark.asyncio
async def test_get_student_grades_summary_no_score(async_session: AsyncSession):
    grades = await get_student_grades_summary(8, session=async_session)
    for g in grades:
        if g['assignment'] == "Assignment 2":
            assert g['score'] is None
            assert g['status'] == "не оценено"

@pytest.mark.asyncio
async def test_get_student_grades_summary_submitted_at_present(async_session: AsyncSession):
    grades = await get_student_grades_summary(8, session=async_session)
    for g in grades:
        assert "submitted_at" in g
        

@pytest.mark.asyncio
async def test_get_student_assignment_details(async_session: AsyncSession):
    details = await get_student_assignment_details(
        telegram_id=8,
        assignment_id=201,
        session=async_session
    )
    assert details["assignment"] == "Assignment 1"
    assert details["course"] == "Course 101"
    assert details["status"] == "сдано"
    assert details["score"] == 90
    assert details["submitted_at"] is not None

    details_overdue = await get_student_assignment_details(
        telegram_id=8,
        assignment_id=202,
        session=async_session
    )
    assert details_overdue["assignment"] == "Assignment 2"
    assert details_overdue["course"] == "Course 101"
    assert details_overdue["status"] == "не сдано"
    assert details_overdue["score"] is None
    assert details_overdue["submitted_at"] is None

    with pytest.raises(ValueError):
        await get_student_assignment_details(
            telegram_id=10,
            assignment_id=201,
            session=async_session
        )

# _get_user_by_username
@pytest.mark.asyncio
async def test__get_user_by_username_found(async_session):
    user = await _get_user_by_username("student_user", async_session)
    assert user is not None
    assert user.telegram_id == 8


@pytest.mark.asyncio
async def test__get_user_by_username_not_found(async_session):
    user = await _get_user_by_username("unknown_user", async_session)
    assert user is None


#_check_permission
@pytest.mark.asyncio
async def test__check_permission_admin_allowed(async_session):
    await _check_permission(6, ["teacher", "assistant", "admin"], 101, async_session)


@pytest.mark.asyncio
async def test__check_permission_user_not_found(async_session):
    with pytest.raises(ValueError):
        await _check_permission(999, ["admin"], 101, async_session)


@pytest.mark.asyncio
async def test__check_permission_banned(async_session):
    user = await async_session.get(User, 8)
    user.banned = True
    await async_session.commit()

    with pytest.raises(AccessDenied):
        await _check_permission(8, ["student"], 101, async_session)


#get_course_students_overview
@pytest.mark.asyncio
async def test_get_course_students_overview_teacher(async_session):
    overview = await get_course_students_overview(
        telegram_id=6,
        course_id=101,
        session=async_session
    )

    assert len(overview) == 1
    student = overview[0]

    assert student["github_username"] == "stud_github"
    assert student["avg_score"] == 90.0
    assert student["not_submitted_count"] == 1
    assert "Assignment 2" in student["not_submitted_assignments"]


#get_assignment_students_status
@pytest.mark.asyncio
async def test_get_assignment_students_status(async_session):
    result = await get_assignment_students_status(
        telegram_id=6,
        assignment_id=201,
        session=async_session
    )

    assert len(result) == 1
    row = result[0]

    assert row["title"] == "Assignment 1"
    assert row["status"] == "оценено"
    assert row["grade"] == 90


@pytest.mark.asyncio
async def test_get_assignment_students_status_not_submitted(async_session):
    result = await get_assignment_students_status(
        telegram_id=6,
        assignment_id=202,
        session=async_session
    )

    assert result[0]["status"] == "не сдано"
    assert result[0]["grade"] is None


@pytest.mark.asyncio
async def test_get_assignment_students_status_no_assignment(async_session):
    result = await get_assignment_students_status(
        telegram_id=6,
        assignment_id=None,
        session=async_session
    )
    assert result == []


#get_classroom_users_without_bot_accounts
@pytest.mark.asyncio
async def test_get_classroom_users_without_bot_accounts(async_session):
    submission = Submission(
        assignment_id=201,
        student_github_username="ghost_user",
        student_telegram_id=None,
        is_submitted=True
    )
    async_session.add(submission)
    await async_session.commit()

    users = await get_classroom_users_without_bot_accounts(
        telegram_id=6,
        course_id=101,
        session=async_session
    )

    assert "ghost_user" in users


#get_course_deadlines_overview
@pytest.mark.asyncio
async def test_get_course_deadlines_overview(async_session):
    overview = await get_course_deadlines_overview(
        telegram_id=6,
        course_id=101,
        session=async_session
    )

    assert len(overview) == 2

    titles = [o["assignment"] for o in overview]
    assert "Assignment 1" in titles
    assert "Assignment 2" in titles

    overdue = next(o for o in overview if o["assignment"] == "Assignment 2")
    assert overdue["submitted_count"] == 0


#get_tasks_to_grade_summary
@pytest.mark.asyncio
async def test_get_tasks_to_grade_summary(async_session: AsyncSession):
    summary = await get_tasks_to_grade_summary(
        telegram_id=6,
        course_id=101,
        session=async_session
    )

    assert len(summary) == 1

    task = summary[0]

    assert task["assignment"] == "Assignment 2"
    assert task["course"] == "Course 101"

    assert task["total_submissions"] == 1
    assert task["graded_count"] == 0
    assert task["to_grade_count"] == 1

    assert task["deadline"] < datetime.now()

