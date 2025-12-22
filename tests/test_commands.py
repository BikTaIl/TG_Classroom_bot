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
    Submission,
    Assistant
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
from commands.teacher_and_assistant_commands import *

DATABASE_URL = "postgresql+asyncpg://bot_admin:5670@localhost/testdb"


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
        student2 = User(
            telegram_id=9,
            telegram_username="student_user_2",
            active_github_username="stud_github_2",
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
        #мб еще отправленное но не оценное задание
        notification1 = Notification(telegram_id=8, notification_time=24)
        notification2 = Notification(telegram_id=8, notification_time=3)
        session.add_all([admin, target, student, student2, permission])
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
    assert user.banned is False


@pytest.mark.asyncio
async def test_create_user_existing(async_session):
    await create_user(1, "testuser", async_session)
    with pytest.raises(ValueError):
        await create_user(1, "testuser", async_session)


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

    with pytest.raises(AccessDenied):
        await set_active_role(2, "assistant", async_session)

    with pytest.raises(AccessDenied):
        await set_active_role(2, "admin", async_session)

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
async def test_change_to_denied_git_account(async_session):
    user1 = User(telegram_id=4, telegram_username="gituser")
    git1 = GithubAccount(github_username="gitlogin", user_telegram_id=4)
    user2 = User(telegram_id=5, telegram_username="gituser2")
    async_session.add_all([user1, git1])
    async_session.add_all([user2])
    await async_session.commit()
    await change_git_account(4, "gitlogin", async_session)
    updated_user = await async_session.get(User, 4)
    assert updated_user.active_github_username == "gitlogin"
    with pytest.raises(ValueError):
        await change_git_account(5, "gitlogin", async_session)

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
async def test_revoke_teacher_role_if_not_exist(async_session):
    with pytest.raises(ValueError):
        await revoke_teacher_role(6, "target_user", async_session)


@pytest.mark.asyncio
async def test_ban_unban_user(async_session):
    await ban_user(6, "target_user", async_session)
    user_stmt = select(User).where(User.telegram_id == 7)
    res = await async_session.execute(user_stmt)
    target = res.scalar_one()
    assert target.banned is True
    with pytest.raises(AccessDenied, match="забанен"):
        await grant_teacher_role(target.telegram_id, "target_user", async_session)
    with pytest.raises(AccessDenied, match="забанен"):
        await get_classroom_users_without_bot_accounts(target.telegram_id, 101, async_session)
    with pytest.raises(AccessDenied, match="забанен"):
        await get_teacher_deadline_notification_payload(target.telegram_id, 201, async_session)
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
    assert "Assignment 2" not in titles


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


@pytest.mark.asyncio
async def test_find_assignments_by_course_id_success(async_session):
    """Успешное получение списка заданий по ID курса"""
    assignments = await find_assignments_by_course_id(101, async_session)
    assert len(assignments) == 2
    assignment_ids = [assignment[0] for assignment in assignments]
    assignment_titles = [assignment[1] for assignment in assignments]
    assert 201 in assignment_ids
    assert 202 in assignment_ids
    assert "Assignment 1" in assignment_titles
    assert "Assignment 2" in assignment_titles


@pytest.mark.asyncio
async def test_find_assignments_by_course_id_none(async_session):
    """Получение заданий с None в качестве course_id"""
    with pytest.raises(ValueError, match="Курс не выбран"):
        await find_assignments_by_course_id(None, async_session)


@pytest.mark.asyncio
async def test_find_assignments_by_course_id_empty(async_session):
    """Получение заданий для курса без заданий"""
    org = await async_session.get(GitOrganization, "Org1")
    empty_course = Course(classroom_id=999, name="Empty Course", organization_name=org.organization_name)
    async_session.add(empty_course)
    await async_session.commit()

    assignments = await find_assignments_by_course_id(999, async_session)
    assert assignments == []


@pytest.mark.asyncio
async def test_find_assignments_by_course_id_not_exist(async_session):
    """Получение заданий для несуществующего курса"""
    assignments = await find_assignments_by_course_id(99999, async_session)
    assert assignments == []


@pytest.mark.asyncio
async def test_find_assistants_courses_success(async_session):
    """Успешное получение списка курсов ассистента"""
    ass_user = User(telegram_id=200)
    async_session.add(ass_user)
    assistant = Assistant(telegram_id=200, course_id=101)
    async_session.add(assistant)
    await async_session.commit()

    courses = await find_assistants_courses(200, async_session)
    assert len(courses) == 1
    assert courses[0][0] == 101
    assert courses[0][1] == "Course 101"


@pytest.mark.asyncio
async def test_find_assistants_courses_multiple(async_session):
    """Получение списка курсов ассистента с несколькими курсами"""
    org = await async_session.get(GitOrganization, "Org1")
    course2 = Course(classroom_id=102, name="Course 102", organization_name=org.organization_name)
    async_session.add(course2)
    await async_session.commit()
    ass_user = User(telegram_id=200)
    async_session.add(ass_user)
    assistant = Assistant(telegram_id=200, course_id=101)
    assistant2 = Assistant(telegram_id=200, course_id=102)
    async_session.add_all([assistant, assistant2])
    await async_session.commit()

    courses = await find_assistants_courses(200, async_session)
    assert len(courses) == 2
    course_ids = [course[0] for course in courses]
    assert 101 in course_ids
    assert 102 in course_ids


@pytest.mark.asyncio
async def test_find_assistants_courses_no_assistant(async_session):
    """Получение курсов для несуществующего ассистента"""

    courses = await find_assistants_courses(999, async_session)
    assert courses == []


@pytest.mark.asyncio
async def test_find_teachers_courses_success(async_session):
    """Успешное получение списка курсов учителя"""
    courses = await find_teachers_courses(6, async_session)
    assert len(courses) == 1
    assert courses[0][0] == 101
    assert courses[0][1] == "Course 101"


@pytest.mark.asyncio
async def test_find_teachers_courses_multiple(async_session):
    """Получение списка курсов учителя с несколькими курсами"""
    org = await async_session.get(GitOrganization, "Org1")
    course2 = Course(classroom_id=102, name="Course 102", organization_name=org.organization_name)
    async_session.add(course2)
    await async_session.commit()

    courses = await find_teachers_courses(6, async_session)
    assert len(courses) == 2
    course_ids = [course[0] for course in courses]
    course_names = [course[1] for course in courses]
    assert 101 in course_ids
    assert 102 in course_ids
    assert "Course 101" in course_names
    assert "Course 102" in course_names


@pytest.mark.asyncio
async def test_find_teachers_courses_no_organization(async_session):
    """Получение курсов учителя без организации"""
    new_teacher = User(telegram_id=100, telegram_username="no_org_teacher")
    async_session.add(new_teacher)
    await async_session.commit()

    with pytest.raises(ValueError, match="Учитель не привязан к организации"):
        await find_teachers_courses(100, async_session)


@pytest.mark.asyncio
async def test_find_assignment_success(async_session):
    """Успешный поиск задания по названию в курсе"""
    assignment_id = await find_assignment(101, "Assignment 1", async_session)
    assert assignment_id == 201


@pytest.mark.asyncio
async def test_find_assignment_not_found(async_session):
    """Поиск несуществующего задания в курсе"""
    with pytest.raises(ValueError, match="Задания с таким именем в данном курсе нет"):
        await find_assignment(101, "Nonexistent Assignment", async_session)


@pytest.mark.asyncio
async def test_find_assignment_different_course(async_session):
    """Поиск задания, существующего в другом курсе"""
    org = await async_session.get(GitOrganization, "Org1")
    course2 = Course(classroom_id=102, name="Course 102", organization_name=org.organization_name)
    assignment3 = Assignment(
        github_assignment_id=203,
        classroom_id=102,
        title="Assignment 3",
        max_score=70,
        deadline_full=datetime.now() + timedelta(days=2)
    )
    async_session.add_all([course2, assignment3])
    await async_session.commit()

    with pytest.raises(ValueError, match="Задания с таким именем в данном курсе нет"):
        await find_assignment(101, "Assignment 3", async_session)


@pytest.mark.asyncio
async def test_find_course_success(async_session):
    """Успешный поиск курса по названию"""
    course_id = await find_course(6, "Course 101", async_session)
    assert course_id == 101


@pytest.mark.asyncio
async def test_find_course_teacher_without_organization(async_session):
    """Поиск курса учителем без привязанной организации"""
    new_teacher = User(telegram_id=100, telegram_username="no_org_teacher")
    async_session.add(new_teacher)
    await async_session.commit()

    with pytest.raises(ValueError, match="Учитель не привязан к организации"):
        await find_course(100, "Course 101", async_session)


@pytest.mark.asyncio
async def test_find_course_not_found(async_session):
    """Поиск несуществующего курса"""
    with pytest.raises(ValueError, match="Курса с таким названием нет"):
        await find_course(6, "Nonexistent Course", async_session)

