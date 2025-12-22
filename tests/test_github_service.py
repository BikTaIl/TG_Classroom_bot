import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from models.db import Base, User, GithubAccount, OAuthState
from infra.git.github_service import (
    login_link_github,
    complete_github_link,
)

DATABASE_URL = "postgresql+asyncpg://molonovboris@localhost:5432/testdb"


@pytest_asyncio.fixture(scope="function")
async def async_session():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with session_maker() as session:
        user = User(telegram_id=1, telegram_username="test_user")
        session.add(user)
        await session.commit()
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_login_link_github_creates_state(async_session):
    url = await login_link_github(telegram_id=1, session=async_session)

    result = await async_session.execute(select(OAuthState))
    state_row = result.scalar_one()

    assert state_row.telegram_id == 1
    assert "github.com/login/oauth/authorize" in url
    assert state_row.state in url


@pytest.mark.asyncio
async def test_complete_github_link_invalid_state(async_session):
    with pytest.raises(ValueError, match="Invalid or expired state"):
        await complete_github_link(
            code="test_code",
            state="wrong_state",
            session=async_session
        )


import httpx

@pytest.mark.asyncio
async def test_complete_github_link_token_http_error(async_session):
    oauth = OAuthState(state="state123", telegram_id=1)
    async_session.add(oauth)
    await async_session.commit()

    with patch("httpx.AsyncClient") as mock_client:
        instance = mock_client.return_value.__aenter__.return_value
        instance.post = AsyncMock(side_effect=httpx.HTTPError("HTTP error"))

        with pytest.raises(RuntimeError, match="GitHub token request failed"):
            await complete_github_link(
                code="code",
                state="state123",
                session=async_session
            )



@pytest.mark.asyncio
async def test_complete_github_link_no_access_token(async_session):
    oauth = OAuthState(state="state123", telegram_id=1)
    async_session.add(oauth)
    await async_session.commit()

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {}

    with patch("httpx.AsyncClient") as mock_client:
        instance = mock_client.return_value.__aenter__.return_value
        instance.post = AsyncMock(return_value=mock_response)

        with pytest.raises(RuntimeError, match="GitHub OAuth failed"):
            await complete_github_link(
                code="code",
                state="state123",
                session=async_session
            )


@pytest.mark.asyncio
async def test_complete_github_link_user_request_error(async_session):
    oauth = OAuthState(state="state123", telegram_id=1)
    async_session.add(oauth)
    await async_session.commit()

    token_response = MagicMock()
    token_response.raise_for_status.return_value = None
    token_response.json.return_value = {"access_token": "token"}

    with patch("httpx.AsyncClient") as mock_client:
        instance = mock_client.return_value.__aenter__.return_value
        instance.post = AsyncMock(return_value=token_response)
        instance.get = AsyncMock(side_effect=httpx.HTTPError("HTTP error"))

        with pytest.raises(RuntimeError):
            await complete_github_link(
                code="code",
                state="state123",
                session=async_session
            )


@pytest.mark.asyncio
async def test_complete_github_link_success(async_session):
    oauth = OAuthState(state="state123", telegram_id=1)
    async_session.add(oauth)
    await async_session.commit()

    token_response = MagicMock()
    token_response.raise_for_status.return_value = None
    token_response.json.return_value = {"access_token": "token123"}

    user_response = MagicMock()
    user_response.raise_for_status.return_value = None
    user_response.json.return_value = {"login": "github_user"}

    with patch("httpx.AsyncClient") as mock_client:
        instance = mock_client.return_value.__aenter__.return_value
        instance.post = AsyncMock(return_value=token_response)
        instance.get = AsyncMock(return_value=user_response)

        github_user = await complete_github_link(
            code="code",
            state="state123",
            session=async_session
        )

    user = await async_session.get(User, 1)
    assert user.active_github_username == "github_user"
    assert github_user["login"] == "github_user"

    res = await async_session.execute(select(OAuthState))
    assert res.scalar_one_or_none() is None

    res = await async_session.execute(select(GithubAccount))
    account = res.scalar_one()
    assert account.github_username == "github_user"