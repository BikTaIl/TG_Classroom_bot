import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, ANY
from aiogram.types import Message, CallbackQuery, User
from aiogram.fsm.context import FSMContext


from commands.common_commands import AccessDenied
from infra.telegram.routers.assistant_router import (
    assistant_panel,
    assistant_summary_panel,
    process_choose_assistant_active_course,
    process_set_assistant_active_course,
    process_previous_page,
    process_next_page, process_choose_assistant_active_assignment, process_set_assistant_active_assignment,
    process_get_course_students_overview_assistant, process_get_assignment_students_status_assistant,
    process_get_classroom_users_without_bot_accounts_assistant,

)


@pytest_asyncio.fixture
def mock_db_session(mocker):
    mock_session = AsyncMock()

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_session
    mock_ctx.__aexit__.return_value = None

    mocker.patch(
        "infra.telegram.routers.assistant_router.AsyncSessionLocal",
        return_value=mock_ctx
    )

    return mock_session



@pytest_asyncio.fixture
def mock_callback():
    cb = AsyncMock(spec=CallbackQuery)
    cb.from_user = User(id=123, is_bot=False, first_name="Test", username="testuser")

    cb.message = AsyncMock(spec=Message)
    cb.message.edit_text = AsyncMock()
    cb.message.answer = AsyncMock()
    cb.message.bot = AsyncMock()
    cb.message.bot.send_message = AsyncMock()

    cb.answer = AsyncMock()
    return cb


@pytest_asyncio.fixture
def mock_message():
    message = AsyncMock(spec=Message)
    message.from_user = User(id=123, is_bot=False, first_name="Test", username="testuser")
    message.text = "some_text"
    message.answer = AsyncMock()
    return message


@pytest_asyncio.fixture
def mock_state():
    state = AsyncMock(spec=FSMContext)
    state._data = {}
    state.get_data = AsyncMock(side_effect=lambda: state._data.copy())
    state.update_data = AsyncMock(side_effect=lambda **kwargs: state._data.update(kwargs))
    state.set_state = AsyncMock()
    state.clear = AsyncMock(side_effect=lambda: state._data.clear())
    return state


@pytest.mark.asyncio
async def test_assistant_panel_success(mock_callback):
    """Тест отображения панели ассистента"""
    await assistant_panel(mock_callback)

    mock_callback.message.edit_text.assert_called_once_with("Панель ассистента:", reply_markup=ANY)
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_assistant_summary_panel_success(mock_callback):
    """Тест отображения панели сводок"""
    await assistant_summary_panel(mock_callback)

    mock_callback.message.edit_text.assert_called_once_with("Выберите сводку:", reply_markup=ANY)
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_choose_assistant_active_course_success(mock_callback, mock_db_session, mocker):
    """Тест выбора курса - успешный сценарий"""
    mock_find_courses = mocker.patch(
        "infra.telegram.routers.assistant_router.find_assistants_courses",
        new_callable=AsyncMock,
        return_value=[(1, "Курс 1")]
    )

    await process_choose_assistant_active_course(mock_callback, mock_callback)

    mock_find_courses.assert_called_once_with(123, mock_db_session)
    mock_callback.message.edit_text.assert_called_once()
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_choose_assistant_active_course_access_denied(mock_callback, mocker):
    """Тест выбора курса - нет доступа"""
    mocker.patch(
        "infra.telegram.routers.assistant_router.find_assistants_courses",
        side_effect=AccessDenied("Нет доступа")
    )

    await process_choose_assistant_active_course(mock_callback, mock_callback)

    mock_callback.message.edit_text.assert_called_once()
    assert "Нет доступа" in mock_callback.message.edit_text.call_args[0][0]
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_choose_assistant_active_assignment_with_course(mock_callback, mock_state, mock_db_session, mocker):
    """Тест выбора задания при наличии активного курса"""
    mock_state.get_data = AsyncMock(return_value={"course_id": 1})
    mock_find_assignments = mocker.patch(
        "infra.telegram.routers.assistant_router.find_assignments_by_course_id",
        new_callable=AsyncMock,
        return_value=[(1, "Задание 1")]
    )

    await process_choose_assistant_active_assignment(mock_callback, mock_state)

    mock_find_assignments.assert_called_once_with(1, mock_db_session)
    mock_callback.message.edit_text.assert_called_once_with("Выберите задание или сбростье его:", reply_markup=ANY)
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_get_course_students_overview_success(mock_callback, mock_state, mock_db_session, mocker):
    """Тест получения сводки по студентам курса"""
    mock_state.get_data = AsyncMock(return_value={"course_id": 1})
    mock_get_overview = mocker.patch(
        "infra.telegram.routers.assistant_router.get_course_students_overview",
        new_callable=AsyncMock,
        return_value=[{"student": "Иван", "progress": "80%"}]
    )
    mock_table_to_text = mocker.patch(
        "infra.telegram.routers.assistant_router.table_to_text",
        new_callable=AsyncMock,
        return_value="Таблица данных"
    )

    await process_get_course_students_overview_assistant(mock_callback, mock_state)

    mock_get_overview.assert_called_once_with(123, 1, mock_db_session)
    mock_table_to_text.assert_called_once()
    mock_callback.message.edit_text.assert_called_once_with(
        "Таблица данных",
        reply_markup=ANY
    )
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_get_assignment_students_status_success(mock_callback, mock_state, mock_db_session, mocker):
    """Тест получения статуса студентов по заданию"""
    mock_state.get_data = AsyncMock(return_value={"assignment_id": 1})
    mock_get_status = mocker.patch(
        "infra.telegram.routers.assistant_router.get_assignment_students_status",
        new_callable=AsyncMock,
        return_value=[{"student": "Иван", "status": "Сдано"}]
    )
    mock_table_to_text = mocker.patch(
        "infra.telegram.routers.assistant_router.table_to_text",
        new_callable=AsyncMock,
        return_value="Таблица cтатусов"
    )

    await process_get_assignment_students_status_assistant(mock_callback, mock_state)

    mock_get_status.assert_called_once_with(123, 1, mock_db_session)
    mock_table_to_text.assert_called_once()
    mock_callback.message.edit_text.assert_called_once_with(
        "Таблица cтатусов",
        reply_markup=ANY
    )
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_get_classroom_users_without_bot_accounts_success(mock_callback, mock_state, mock_db_session, mocker):
    """Тест получения пользователей без аккаунтов бота"""
    mock_state.get_data = AsyncMock(return_value={"course_id": 1})
    mock_get_users = mocker.patch(
        "infra.telegram.routers.assistant_router.get_classroom_users_without_bot_accounts",
        new_callable=AsyncMock,
        return_value=["user1", "user2", "user3"]
    )

    await process_get_classroom_users_without_bot_accounts_assistant(mock_callback, mock_state)

    mock_get_users.assert_called_once_with(123, 1, mock_db_session)
    mock_callback.message.edit_text.assert_called_once()
    text = mock_callback.message.edit_text.call_args[0][0]
    assert "user1" in text
    assert "user2" in text
    assert "user3" in text
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("handler", [
    process_choose_assistant_active_course,
    process_get_course_students_overview_assistant,
    process_get_assignment_students_status_assistant,
    process_get_classroom_users_without_bot_accounts_assistant,
])
async def test_handlers_access_denied(handler, mock_callback, mock_state, mocker):
    """Общий тест для обработки AccessDenied во всех обработчиках"""
    for func_name in [
        "find_assistants_courses",
        "get_course_students_overview",
        "get_assignment_students_status",
        "get_classroom_users_without_bot_accounts",
    ]:
        mocker.patch(
            f"infra.telegram.routers.assistant_router.{func_name}",
            side_effect=AccessDenied("Доступ запрещен")
        )
    if handler in [process_choose_assistant_active_course,
                    process_get_course_students_overview_assistant,
                    process_get_assignment_students_status_assistant,
                    process_get_classroom_users_without_bot_accounts_assistant]:
        mock_state.get_data = AsyncMock(return_value={"course_id": 1, "assignment_id": 2})

    if handler == process_set_assistant_active_course:
        mock_callback.data = "set_assistant_active_course:1"

    await handler(mock_callback, mock_state)

    mock_callback.message.edit_text.assert_called_once()
    assert "Доступ запрещен" in mock_callback.message.edit_text.call_args[0][0]
    mock_callback.answer.assert_called_once()


