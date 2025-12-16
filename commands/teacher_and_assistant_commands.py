from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Any, Sequence, Mapping


async def set_teacher_active_course(telegram_id: int, course_id: Optional[int], session: AsyncSession) -> None:
    """Установить/сбросить активный курс пользователя."""


async def set_teacher_active_assignment(telegram_id: int, assignment_id: Optional[int], session: AsyncSession) -> None:
    """Установить/сбросить активное задание для пользователя."""


async def get_course_students_overview(
        telegram_id: int,
        session: AsyncSession,
        course_id: Optional[int] = None
) -> Sequence[Mapping[str, Any]]:
    """Сводка: ФИО, Курс, GitHub, просрочки, средний балл, дата последнего коммита. Сортировка по ФИО и названию курса (в соответствующем порядке)"""


async def get_assignment_students_status(
        telegram_id: int,
        session: AsyncSession,
        assignment_id: Optional[int] = None
) -> Sequence[Mapping[str, Any]]:
    """Сводка по отдельному заданию: ФИО, GitHub, статус. Сортировка по статусу и ФИО"""


async def get_classroom_users_without_bot_accounts(
        telegram_id: int,
        session: AsyncSession,
        course_id: Optional[int] = None
) -> Sequence[str]:
    """GitHub-логины студентов, которых нет в боте. Таковыми считаем тех, кто хоть что-то сдавал по некоторому заданию"""


async def get_course_deadlines_overview(
        telegram_id: int,
        session: AsyncSession,
        course_id: Optional[int] = None
) -> Sequence[Mapping[str, Any]]:
    """Сводка всех дедлайнов. Сортировка по дд"""


async def get_tasks_to_grade_summary(
        telegram_id: int,
        session: AsyncSession,
        course_id: Optional[int] = None
) -> Sequence[Mapping[str, Any]]:
    """Сводка по задачам, которые нужно оценить. Сортировка по дд и названию курса"""


async def get_manual_check_submissions_summary(
        telegram_id: int,
        session: AsyncSession,
        course_id: Optional[int] = None
) -> Sequence[Mapping[str, Any]]:
    """Сводка по ручной проверке: ФИО, GitHub, даты сдачи и дедлайна. Сортировка по дд и названию курса"""


async def get_teacher_deadline_notification_payload(
        teacher_telegram_id: int,
        assignment_id: int,
        session: AsyncSession
) -> Optional[Mapping[str, Any]]:
    """Данные для уведомления: сколько не сдали, список студентов, дедлайн."""


async def add_course_assistant(
        teacher_telegram_id: int,
        course_id: int,
        assistant_telegram_username: str,
        session: AsyncSession
) -> None:
    """Добавить ассистента по username. Только для учителя"""


async def remove_course_assistant(
        teacher_telegram_id: int,
        course_id: int,
        assistant_telegram_username: str,
        session: AsyncSession
) -> None:
    """Удалить ассистента. Только для учителя"""


async def create_course_announcement(
        teacher_telegram_id: int,
        course_id: int,
        text: str,
        session: AsyncSession
) -> None:
    """Создать объявление для курса. Только для учителя"""


async def trigger_manual_sync_for_teacher(
        course_id: int,
        teacher_telegram_id: int,
        session: AsyncSession
        ) -> bool:
        """Выполнить ручную синхронизацию данных по курсу. Только для учителя"""