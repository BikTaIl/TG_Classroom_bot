from typing import Optional, Sequence, Mapping, Any
from datetime import datetime, date
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from decimal import Decimal

from models.db import User, GithubAccount, Notification, Course, Assignment, Assistant, Submission, Permission, \
    ErrorLog, AccessDenied

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
        

async def login_link_github(telegram_id: int, session: AsyncSession) -> str:
    """Вернуть URL для привязки GitHub-аккаунта к пользователю Telegram."""
    pass


async def complete_github_link(telegram_id: int, code: str, state: str, session: AsyncSession) -> None:
    """Завершить привязку GitHub-аккаунта после редиректа от GitHub"""
    pass


async def logout_user(telegram_id: int, session: AsyncSession) -> None:
    pass


async def set_active_role(telegram_id: int, role: str, session: AsyncSession) -> None:
    """Установить активную роль пользователя: 'student', 'teacher', 'assistant', 'admin'. С проверкой на доступность роли"""
    pass  # жду деталей реализации


async def toggle_global_notifications(telegram_id: int, session: AsyncSession) -> None:
    """Глобально сменить рычажок уведомлений по дд для пользователя."""
    user = await session.get(User, telegram_id)
    if user:
        user.notifications_enabled = not user.notifications_enabled
        await session.commit()
    else:
        raise ValueError(f"Пользователя {telegram_id} не существует.")


async def change_git_account(telegram_id: int, github_login: str, session: AsyncSession) -> None:
    """Сменить гитхаб-аккаунт на другой залогиненный"""
    pass

async def enter_name(telegram_id: int, full_name: str, session: AsyncSession) -> None:
    """Добавить в бд полное имя пользователся"""
    user = await session.get(User, telegram_id)
    user.full_name = full_name
    await session.commit()
