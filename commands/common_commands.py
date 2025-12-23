from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.db import User, GithubAccount, Permission, AccessDenied


async def create_user(telegram_id: int, telegram_username: str, session: AsyncSession) -> None:
    """"Создать профиль юзера при старте"""
    async with session.begin():
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                telegram_id=telegram_id,
                telegram_username=telegram_username,
                active_role=None,
                sync_count=0,
                active_github_username=None,
                full_name=None,
                banned=False,
                notifications_enabled=True,
            )
            session.add(user)
        else:
            raise ValueError("Пользователь уже существует.")


async def create_permission_student(telegram_id: int, session: AsyncSession) -> None:
    async with session.begin():
        result_perm = await session.execute(
            select(Permission).where(Permission.telegram_id == telegram_id,
                                     Permission.permitted_role == 'student')
        )
        permission = result_perm.scalar_one_or_none()
        if permission is None:
            permission = Permission(
                telegram_id=telegram_id,
                permitted_role='student'
            )
            session.add(permission)
        else:
            raise ValueError("Разрешение уже выдано")


async def set_active_role(telegram_id: int, role: str, session: AsyncSession) -> None:
    """Установить активную роль пользователя: 'student', 'teacher', 'assistant', 'admin'. С проверкой на доступность роли"""
    async with session.begin():
        user = await session.get(User, telegram_id)
        if not user:
            raise ValueError(f"Пользователя {telegram_id} не существует.")
        if role not in ['student', 'teacher', 'assistant', 'admin']:
            raise ValueError("Такой роли не существует.")
        permission_query = select(Permission).where(
            (Permission.telegram_id == telegram_id) &
            (Permission.permitted_role == role)
        )
        result = await session.execute(permission_query)
        permission = result.scalar_one_or_none()
        if not permission:
            raise AccessDenied("У вас нет доступа к этой роли.")
        user.active_role = role


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
    user = await session.get(User, telegram_id)
    if not user:
        raise ValueError(f"Пользователя {telegram_id} не существует.")
    git_query = select(GithubAccount).where(and_(
        GithubAccount.github_username == github_login,
        GithubAccount.user_telegram_id == telegram_id
    ))
    query = await session.execute(git_query)
    git = query.scalar_one_or_none()
    if not git:
        raise ValueError(f"Аккаунта {github_login} не существует или у вас нет к нему доступа.")
    user.active_github_username = github_login


async def enter_name(telegram_id: int, full_name: str, session: AsyncSession) -> None:
    """Добавить в бд полное имя пользователся"""
    user = await session.get(User, telegram_id)
    user.full_name = full_name
    await session.commit()
