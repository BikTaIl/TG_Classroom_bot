import os
import secrets
import aiohttp
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlencode
from sqlalchemy import select
#from models.db import User, GithubAccount, Permission, ErrorLog
from dotenv import load_dotenv
import httpx

load_dotenv()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

async def login_link_github(telegram_id: int
                            #,session: AsyncSession
                            ) -> str:
    """Вернуть URL для привязки GitHub-аккаунта к пользователю Telegram."""
    state = str(telegram_id)

    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "read:user repo",
        "state": state,
        "allow_signup": "true"
    }

    auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    return auth_url


async def complete_github_link(telegram_id: int,
                               code: str, state: str
                               #, session: AsyncSession
                               ) -> None:
    """Завершить привязку GitHub-аккаунта после редиректа от GitHub"""
    # Проверка, что state соответствует telegram_id (CSRF)
    if state != str(telegram_id):
        raise ValueError("Invalid state parameter")

    # Обмен code на access token
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "state": state
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=payload, headers=headers)
        resp.raise_for_status()
        token_data = resp.json()

    access_token = token_data.get("access_token")
    if not access_token:
        raise RuntimeError(f"GitHub OAuth failed: {token_data}")

    # Получаем данные пользователя с GitHub
    user_url = "https://api.github.com/user"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        resp = await client.get(user_url, headers=headers)
        resp.raise_for_status()
        github_user = resp.json()

    login = github_user["login"]

    return github_user

    github_username = github_user["login"]
    full_name = github_user.get("name") or github_username

    # Сохраняем или обновляем пользователя и GitHub аккаунт
    # try:
    #     user = (await session.execute(
    #         select(User).where(User.telegram_id == telegram_id)
    #     )).scalar_one()
    # except NoResultFound:
    #     # Если пользователя нет, создаем
    #     user = User(
    #         telegram_id=telegram_id,
    #         full_name=full_name,
    #         active_github_username=github_username,
    #         banned=False,
    #         notifications_enabled=True
    #     )
    #     session.add(user)
    #     await session.commit()
    # else:
    #     # Если есть — обновляем данные
    #     user.active_github_username = github_username
    #     user.full_name = full_name
    #     await session.commit()
    #
    # # Сохраняем GitHub аккаунт
    # gh_account = (await session.execute(
    #     select(GithubAccount).where(GithubAccount.github_username == github_username)
    # )).scalar_one_or_none()
    #
    # if not gh_account:
    #     gh_account = GithubAccount(
    #         github_username=github_username,
    #         user_telegram_id=telegram_id
    #     )
    #     session.add(gh_account)
    #     await session.commit()

async def logout_user(telegram_id: int, session: AsyncSession) -> None:
    """Разлогинить текущий акк из GitHub."""


async def set_active_role(telegram_id: int, role: str, session: AsyncSession) -> None:
    """Установить активную роль пользователя: 'student', 'teacher', 'assistant', 'admin'. С проверкой на доступность роли"""


async def toggle_global_notifications(telegram_id: int, session: AsyncSession) -> None:
    """Глобально сменить рычажок уведомлений по дд для пользователя."""


async def change_git_account(telegram_id: int, github_login: str, session: AsyncSession) -> None:
    """Сменить гитхаб-аккаунт на другой залогиненный"""



from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio
from uvicorn import Config, Server

async def start_fastapi():
    config = Config("auth_api.auth_service:app", host="127.0.0.1", port=8000, loop="asyncio")
    server = Server(config)
    await server.serve()

async def start_auth():
    telegram_id = 123456  # для теста
    url = await login_link_github(telegram_id)
    print("Перейдите по ссылке для авторизации GitHub:")
    print(url)


async def main():
    await asyncio.gather(
        start_fastapi(),
        start_auth()
    )

if __name__ == "__main__":
    asyncio.run(main())