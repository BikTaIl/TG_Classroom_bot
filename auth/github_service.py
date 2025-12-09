import os
import secrets
import aiohttp
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlencode
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

    print(github_user)

    login = github_user["login"]

    return github_user

async def start_auth():
    telegram_id = 123456  # для теста
    url = await login_link_github(telegram_id)
    print("Перейдите по ссылке для авторизации GitHub:")
    print(url)
