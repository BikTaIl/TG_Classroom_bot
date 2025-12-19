import secrets
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlencode
import httpx
from models.db import (User, GithubAccount, OAuthState)
from infra.config import GITHUB_CLIENT_ID, REDIRECT_URI, GITHUB_CLIENT_SECRET

async def login_link_github(telegram_id: int, session: AsyncSession) -> str:
    """Вернуть URL для привязки GitHub-аккаунта к пользователю Telegram."""
    state = secrets.token_urlsafe(32)

    oauth_state = OAuthState(
        state=state,
        telegram_id=telegram_id
    )
    async with session.begin():
        session.add(oauth_state)

    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "read:user repo",
        "state": state,
        "allow_signup": "true"
    }

    auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    return auth_url


async def complete_github_link(code: str, state: str, session: AsyncSession) -> None:
    """Завершить привязку GitHub-аккаунта после редиректа от GitHub"""
    async with session.begin():
        result = await session.execute(
            select(OAuthState).where(OAuthState.state == state)
        )
        state_row = result.scalar_one_or_none()

        if state_row is None:
            raise ValueError("Invalid or expired state")
        telegram_id = state_row.telegram_id

    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "state": state
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(token_url, data=payload, headers=headers)
            resp.raise_for_status()
            token_data = resp.json()
    except httpx.HTTPError as e:
        raise RuntimeError(f"GitHub token request failed: {e}")

    access_token = token_data.get("access_token")
    if not access_token:
        raise RuntimeError(f"GitHub OAuth failed: {token_data}")
    #Рейз статуса
    user_url = "https://api.github.com/user"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(user_url, headers=headers)
            resp.raise_for_status()
            github_user = resp.json()
    except httpx.HTTPError as e:
        raise RuntimeError(f"GitHub token request failed: {e}")

    async with session.begin():
        user = await session.get(User, telegram_id)
        #рейз статуса
        if user is None:
            raise ValueError("Wrong telegram_id passed")

        result = await session.execute(
            select(GithubAccount).where(
                GithubAccount.github_username == github_user["login"],
                GithubAccount.user_telegram_id == telegram_id,
            )
        )
        account = result.scalar_one_or_none()

        if account is None:
            account = GithubAccount(
                github_username=github_user["login"],
                user_telegram_id=telegram_id,
            )
            session.add(account)

        user.active_github_username = github_user["login"]
        await session.execute(
            delete(OAuthState).where(OAuthState.state == state)
        )
    return github_user
