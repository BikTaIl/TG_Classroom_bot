from typing import Optional, Mapping, Any
from datetime import datetime, date
from sqlalchemy import select, delete, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from .teacher_and_assistant_commands import _check_permission, _get_user_by_username
from models.db import Permission, ErrorLog, GitLogs, GitOrganization

SUCCESS_STATUS = 200


async def grant_teacher_role(
        admin_telegram_id: int,
        target_telegram_username: str,
        session: AsyncSession = None
) -> None:
    """Выдать роль teacher."""
    await _check_permission(admin_telegram_id, ['admin'], 0, session)

    if target_telegram_username[0] == '@':
        target_telegram_username = target_telegram_username[1:]
    user = await _get_user_by_username(target_telegram_username, session)
    if not user:
        raise ValueError(f"Пользователь {target_telegram_username} не найден")

    stmt = select(Permission).where(
        and_(
            Permission.telegram_id == user.telegram_id,
            Permission.permitted_role == 'teacher'
        )
    )
    result = await session.execute(stmt)
    existing_permission = result.scalar_one_or_none()

    if existing_permission:
        raise ValueError(f"Пользователь {target_telegram_username} уже имеет роль teacher")

    permission = Permission(
        telegram_id=user.telegram_id,
        permitted_role='teacher'
    )
    session.add(permission)
    await session.commit()


async def revoke_teacher_role(
        admin_telegram_id: int,
        target_telegram_username: str,
        session: AsyncSession = None
) -> None:
    """Отобрать роль teacher."""
    await _check_permission(admin_telegram_id, ['admin'], 0, session)
    if target_telegram_username[0] == '@':
        target_telegram_username = target_telegram_username[1:]
    user = await _get_user_by_username(target_telegram_username, session)
    if not user:
        raise ValueError(f"Пользователь {target_telegram_username} не найден")

    existing_query = select(Permission).where(
        (Permission.telegram_id == user.telegram_id) &
        (Permission.permitted_role == 'teacher')
    )
    existing_result = await session.execute(existing_query)
    existing_permission = existing_result.scalar_one_or_none()
    if not existing_permission:
        raise ValueError(f"У пользователя {target_telegram_username} нет роли 'teacher'")
    stmt = delete(Permission).where(
        and_(
            Permission.telegram_id == user.telegram_id,
            Permission.permitted_role == 'teacher'
        )
    )
    await session.execute(stmt)
    await session.commit()


async def ban_user(
        admin_telegram_id: int,
        target_telegram_username: str,
        session: AsyncSession = None
) -> None:
    """Забанить пользователя."""
    await _check_permission(admin_telegram_id, ['admin'], 0, session)
    if target_telegram_username[0] == '@':
        target_telegram_username = target_telegram_username[1:]
    user = await _get_user_by_username(target_telegram_username, session)
    if not user:
        raise ValueError(f"Пользователь {target_telegram_username} не найден")

    if user.banned:
        raise ValueError(f"Пользователь {target_telegram_username} уже забанен")

    user.banned = True
    await session.commit()


async def unban_user(
        admin_telegram_id: int,
        target_telegram_username: str,
        session: AsyncSession = None
) -> None:
    """Разбанить пользователя."""
    await _check_permission(admin_telegram_id, ['admin'], 0, session)
    if target_telegram_username[0] == '@':
        target_telegram_username = target_telegram_username[1:]
    user = await _get_user_by_username(target_telegram_username, session)
    if not user:
        raise ValueError(f"Пользователь {target_telegram_username} не найден")

    if not user.banned:
        raise ValueError(f"Пользователь {target_telegram_username} не забанен")

    user.banned = False
    await session.commit()


async def get_error_count_for_day(
        admin_telegram_id: int,
        day: Optional[date] = None,
        session: AsyncSession = None
) -> int:
    """Количество ошибок бота за указанный день, либо вся сводка ошибок.
    Сортировка по дате по убыванию."""
    await _check_permission(admin_telegram_id, ['admin'], 0, session)
    if day:
        start_date = datetime.combine(day, datetime.min.time())
        end_date = datetime.combine(day, datetime.max.time())

        stmt = select(func.count(ErrorLog.id)).where(
            and_(
                ErrorLog.created_at >= start_date,
                ErrorLog.created_at <= end_date
            )
        )
        result = await session.execute(stmt)
        return result.scalar() or 0
    else:
        stmt = select(
            func.date(ErrorLog.created_at).label('error_date'),
            func.count(ErrorLog.id).label('error_count')
        ).group_by(
            func.date(ErrorLog.created_at)
        ).order_by(
            desc(func.date(ErrorLog.created_at))
        )

        result = await session.execute(stmt)
        errors_by_day = result.all()

        return len(errors_by_day)


async def get_last_successful_github_call_time(
        admin_telegram_id: int,
        session: AsyncSession = None
) -> Optional[datetime]:
    """Последнее успешное обращение к GitHub."""
    await _check_permission(admin_telegram_id, ['admin'], 0, session)

    stmt = select(GitLogs).where(
        GitLogs.log_status == SUCCESS_STATUS
    ).order_by(
        desc(GitLogs.created_at)
    ).limit(1)

    result = await session.execute(stmt)
    last_log = result.scalar_one_or_none()

    return last_log.created_at if last_log else None


async def get_last_failed_github_call_info(
        admin_telegram_id: int,
        session: AsyncSession = None
) -> Optional[Mapping[str, Any]]:
    """Информация о последнем ошибочном обращении к GitHub."""
    await _check_permission(admin_telegram_id, ['admin'], 0, session)

    stmt = select(GitLogs).where(
        GitLogs.log_status != SUCCESS_STATUS
    ).order_by(
        desc(GitLogs.created_at)
    ).limit(1)

    result = await session.execute(stmt)
    last_failed_log = result.scalar_one_or_none()

    if not last_failed_log:
        return None

    return {
        "timestamp": last_failed_log.created_at,
        "status": last_failed_log.log_status,
        "message": last_failed_log.log_message
    }


async def add_organisation(admin_telegram_id: int, teacher_telegram_id: int, name: str,
                           session: AsyncSession = None) -> None:
    await _check_permission(admin_telegram_id, ['admin'], 0, session)
    query = await session.execute(select(GitOrganization).where(GitOrganization.organization_name == name))
    existing = query.scalar_one_or_none()
    if existing:
        raise ValueError("Организация уже существует.")
    new_organization = GitOrganization(
        organization_name=name,
        teacher_telegram_id=teacher_telegram_id
    )
    session.add(new_organization)
    await session.commit()

async def delete_organization(admin_telegram_id: int, name: str, session: AsyncSession = None) -> None:
    pass