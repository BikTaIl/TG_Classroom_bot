import os
import secrets
import aiohttp
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession


async def logout_user(telegram_id: int, session: AsyncSession) -> None:
    """Разлогинить текущий акк из GitHub."""


async def set_active_role(telegram_id: int, role: str, session: AsyncSession) -> None:
    """Установить активную роль пользователя: 'student', 'teacher', 'assistant', 'admin'. С проверкой на доступность роли"""


async def toggle_global_notifications(telegram_id: int, session: AsyncSession) -> None:
    """Глобально сменить рычажок уведомлений по дд для пользователя."""


async def change_git_account(telegram_id: int, github_login: str, session: AsyncSession) -> None:
    """Сменить гитхаб-аккаунт на другой залогиненный"""
