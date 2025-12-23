import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, ANY
from aiogram.types import Message, CallbackQuery, User
from aiogram.fsm.context import FSMContext

from infra.telegram.routers.common_router import (
    start_panel,
    return_to_start_panel,
    process_login_link_github,
    process_logout_user,
    process_set_active_role_first,
    process_set_active_role_student,
    process_set_active_role_teacher,
    process_set_active_role_admin,
    process_set_active_role_assistant,
    process_toggle_global_notifications,
    process_change_git_account_first,
    process_change_git_account_second,
    process_enter_name_first,
    process_enter_name_second,
)

from infra.telegram.routers.states import(
    EnterName,
    ChangeGitHubAccount,
)

from commands.common_commands import AccessDenied


@pytest_asyncio.fixture
def mock_db_session(mocker):
    mock_session = AsyncMock()

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_session
    mock_ctx.__aexit__.return_value = None

    mocker.patch(
        "infra.telegram.routers.common_router.AsyncSessionLocal",
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
    return AsyncMock(spec=FSMContext)


@pytest.mark.asyncio
async def test_start_command_success(mock_message, mock_db_session, mocker):
    mock_create_user = mocker.patch(
        "infra.telegram.routers.common_router.create_user",
        new_callable=AsyncMock
    )
    mock_create_perm = mocker.patch(
        "infra.telegram.routers.common_router.create_permission_student",
        new_callable=AsyncMock
    )

    await start_panel(mock_message)

    mock_create_user.assert_called_once_with(
        123,
        "testuser",
        ANY
    )
    mock_create_perm.assert_called_once_with(
        123,
        ANY
    )

    mock_message.answer.assert_called_once()
    assert "Основная панель" in mock_message.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_return_to_start_panel_callback(mock_callback):
    await return_to_start_panel(mock_callback)

    mock_callback.message.answer.assert_called_once()
    assert "Основная панель" in mock_callback.message.answer.call_args[0][0]

    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_login_link_github_success(mock_callback, mock_state, mock_db_session, mocker):
    mock_login = mocker.patch(
        "infra.telegram.routers.common_router.login_link_github",
        new_callable=AsyncMock,
        return_value="http://github.com/auth"
    )

    await process_login_link_github(mock_callback, mock_state)

    mock_login.assert_called_once_with(123, ANY)
    mock_callback.message.edit_text.assert_called_once()
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_login_link_github_access_denied(mock_callback, mock_state, mocker):
    mocker.patch(
        "infra.telegram.routers.common_router.login_link_github",
        side_effect=AccessDenied("Нет доступа")
    )

    await process_login_link_github(mock_callback, mock_state)

    mock_callback.message.edit_text.assert_called_once()
    assert "Нет доступа" in mock_callback.message.edit_text.call_args[0][0]
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_logout_user_success(mock_callback, mock_state, mock_db_session, mocker):
    mocker.patch(
        "infra.telegram.routers.common_router.login_link_github",
        new_callable=AsyncMock
    )

    await process_logout_user(mock_callback, mock_state)

    mock_callback.message.edit_text.assert_called_once()
    assert "Аккаунт разлогинен" in mock_callback.message.edit_text.call_args[0][0]
    mock_callback.answer.assert_called_once()



@pytest.mark.asyncio
async def test_process_set_active_role_first(mock_callback, mock_state):
    await process_set_active_role_first(mock_callback, mock_state)
    mock_callback.message.edit_text.assert_called_once()

    assert "Выберите одну из возможных ролей" in \
           mock_callback.message.edit_text.call_args[0][0]

    mock_callback.answer.assert_called_once()



@pytest.mark.asyncio
@pytest.mark.parametrize(
    "handler, role_text, method",
    [
        (process_set_active_role_student, "студент", "answer"),
        (process_set_active_role_teacher, "учитель", "edit_text"),
        (process_set_active_role_admin, "администратор", "edit_text"),
        (process_set_active_role_assistant, "ассистент", "edit_text"),
    ]
)
async def test_set_role_success(
    handler,
    role_text,
    method,
    mock_callback,
    mock_state,
    mock_db_session,
    mocker
):
    mocker.patch(
        "infra.telegram.routers.common_router.set_active_role",
        new_callable=AsyncMock
    )

    await handler(mock_callback, mock_state)

    message_method = getattr(mock_callback.message, method)
    message_method.assert_called_once()
    assert role_text in message_method.call_args[0][0]

    mock_callback.answer.assert_called_once()



@pytest.mark.asyncio
async def test_set_role_access_denied(mock_callback, mock_state, mocker):
    mocker.patch(
        "infra.telegram.routers.common_router.set_active_role",
        side_effect=AccessDenied("Нет прав")
    )

    await process_set_active_role_student(mock_callback, mock_state)

    mock_callback.message.answer.assert_called_once()
    assert "Нет прав" in mock_callback.message.answer.call_args[0][0]
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_toggle_notifications_success(mock_callback, mock_state, mock_db_session, mocker):
    mocker.patch(
        "infra.telegram.routers.common_router.toggle_global_notifications",
        new_callable=AsyncMock
    )

    await process_toggle_global_notifications(mock_callback, mock_state)

    mock_callback.message.edit_text.assert_called_once()
    assert "уведомлений" in mock_callback.message.edit_text.call_args[0][0]
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_process_change_git_account_first(mock_callback, mock_state):
    await process_change_git_account_first(mock_callback, mock_state)

    mock_state.set_state.assert_called_once_with(
        ChangeGitHubAccount.waiting_login
    )

    mock_callback.message.edit_text.assert_called_once()
    assert "Введи логин гитхаба" in \
           mock_callback.message.edit_text.call_args[0][0]

    mock_callback.answer.assert_called_once()



@pytest.mark.asyncio
async def test_change_git_account_second_success(mock_message, mock_state, mock_db_session, mocker):
    mock_message.text = "new_login"

    mock_change = mocker.patch(
        "infra.telegram.routers.common_router.change_git_account",
        new_callable=AsyncMock
    )

    await process_change_git_account_second(mock_message, mock_state)

    mock_change.assert_called_once_with(123, "new_login", ANY)
    mock_message.answer.assert_called_once()
    mock_state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_change_git_account_second_error(mock_message, mock_state, mocker):
    mock_message.text = "bad_login"

    mocker.patch(
        "infra.telegram.routers.common_router.change_git_account",
        side_effect=ValueError("Ошибка")
    )

    await process_change_git_account_second(mock_message, mock_state)

    mock_message.answer.assert_called_once()
    assert "Ошибка" in mock_message.answer.call_args[0][0]
    mock_state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_process_enter_name_first(mock_callback, mock_state):
    await process_enter_name_first(mock_callback, mock_state)

    mock_state.set_state.assert_called_once_with(
        EnterName.waiting_name
    )

    mock_callback.message.edit_text.assert_called_once()
    assert "Введите свое ФИО" in \
           mock_callback.message.edit_text.call_args[0][0]

    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_process_enter_name_second_success(
    mock_message,
    mock_state,
    mock_db_session,
    mocker
):
    mock_enter_name = mocker.patch(
        "infra.telegram.routers.common_router.enter_name",
        new_callable=AsyncMock
    )
    await process_enter_name_second(mock_message, mock_state)

    mock_enter_name.assert_called_once_with(
        123,
        mock_message.text,
        mock_db_session
    )

    mock_message.answer.assert_called_once()
    assert "ФИО успешно получено" in \
           mock_message.answer.call_args[0][0]

    mock_state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_process_enter_name_second_access_denied(
    mock_message,
    mock_state,
    mock_db_session,
    mocker
):
    mock_enter_name = mocker.patch(
        "infra.telegram.routers.common_router.enter_name",
        new_callable=AsyncMock,
        side_effect=AccessDenied("Нет доступа")
    )

    await process_enter_name_second(mock_message, mock_state)

    mock_message.answer.assert_called_once()
    assert "Нет доступа" in \
           mock_message.answer.call_args[0][0]

    mock_state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_process_enter_name_second_value_error(
    mock_message,
    mock_state,
    mock_db_session,
    mocker
):
    mock_enter_name = mocker.patch(
        "infra.telegram.routers.common_router.enter_name",
        new_callable=AsyncMock,
        side_effect=ValueError("Некорректное ФИО")
    )

    await process_enter_name_second(mock_message, mock_state)

    mock_message.answer.assert_called_once()
    assert "Некорректное ФИО" in \
           mock_message.answer.call_args[0][0]

    mock_state.clear.assert_called_once()


