from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Mapping, Any
from datetime import date, datetime

async def grant_teacher_role(admin_telegram_id: int, target_telegram_username: str,
                             session: AsyncSession) -> None:
    """Выдать роль teacher."""


async def revoke_teacher_role(admin_telegram_id: int, target_telegram_username: str,
                              session: AsyncSession) -> None:
    """Отобрать роль teacher."""


async def ban_user(admin_telegram_id: int, target_telegram_username: str,
                   session: AsyncSession) -> None:
    """Забанить пользователя."""


async def unban_user(admin_telegram_id: int, target_telegram_username: str,
                     session: AsyncSession) -> None:
    """Разбанить пользователя."""


async def get_error_count_for_day(admin_telegram_id: int, session: AsyncSession,
                                  day: Optional[date] = None) -> int:
    """Количество ошибок бота за указанный день, либо вся сводка ошибок. Сортировка по дате по убыванию."""


async def get_last_successful_github_call_time(admin_telegram_id: int,
                                               session: AsyncSession) -> Optional[datetime]:
    """Последнее успешное обращение к GitHub."""


async def get_last_failed_github_call_info(admin_telegram_id: int,
                                           session: AsyncSession) -> Optional[Mapping[str, Any]]:
    """Информация о последнем ошибочном обращении к GitHub."""