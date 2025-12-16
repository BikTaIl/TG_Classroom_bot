import os
import secrets
import aiohttp
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.db import User

async def create_user(telegram_id: int, telegram_username: str, session: AsyncSession) -> None:
    """"Создать профиль юзера при старте"""
    async with session.begin():
        new_user: User = User(
            telegram_id=telegram_id,
            telegram_username = telegram_username,
            active_role = None,
            active_github_username = None,
            full_name = None,
            banned = False,
            notifications_enabled = True
        )
        session.add(new_user)

async def logout_user(telegram_id: int, session: AsyncSession) -> None:
    """Разлогинить текущий акк из GitHub."""


async def set_active_role(telegram_id: int, role: str, session: AsyncSession) -> None:
    """Установить активную роль пользователя: 'student', 'teacher', 'assistant', 'admin'. С проверкой на доступность роли"""


async def toggle_global_notifications(telegram_id: int, session: AsyncSession) -> None:
    """Глобально сменить рычажок уведомлений по дд для пользователя."""


async def change_git_account(telegram_id: int, github_login: str, session: AsyncSession) -> None:
    """Сменить гитхаб-аккаунт на другой залогиненный"""

async def enter_name(telegram_id: int, name: str, session: AsyncSession) -> None:
    """Ввести ФИО"""