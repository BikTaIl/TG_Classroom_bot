import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models.db import Base, User, GithubAccount, Permission, AccessDenied
from commands.common_commands import (
    create_user,
    set_active_role,
    toggle_global_notifications,
    change_git_account,
    enter_name,
)

DATABASE_URL = "postgresql+asyncpg://bot_admin@localhost:5433/testdb"


@pytest_asyncio.fixture(scope="function")
async def async_session():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session_maker() as session:
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
