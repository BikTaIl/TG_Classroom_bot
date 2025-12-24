import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, ANY
from aiogram.types import Message, CallbackQuery, User
from aiogram.fsm.context import FSMContext

from infra.telegram.routers.teacher_router import *
from infra.telegram.routers.states import AddAssistant, RemoveAssistant, AddAnnouncement

from commands.common_commands import AccessDenied


@pytest_asyncio.fixture
def mock_db_session(mocker):
    mock_session = AsyncMock()

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_session
    mock_ctx.__aexit__.return_value = None

    mocker.patch(
        "infra.telegram.routers.teacher_router.AsyncSessionLocal",
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
    cb.data = AsyncMock(spec=str)

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
    state.update_data = AsyncMock()
    return state


@pytest.mark.asyncio
async def test_teacher_panel_success(mock_callback):
    """Тест отображения панели учителя"""
    await teacher_panel(mock_callback)

    mock_callback.message.edit_text.assert_called_once_with("Панель учителя:")
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_teacher_summary_panel_success(mock_callback):
    """Тест отображения панели сводок"""
    await teacher_summary_panel(mock_callback)

    mock_callback.message.edit_text.assert_called_once_with("Выберите сводку:")
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_choose_teacher_active_course_success(mock_callback, mock_db_session, mocker):
    """Тест выбора курса - успешный сценарий"""
    mock_find_courses = mocker.patch(
        "infra.telegram.routers.teacher_router.find_teachers_courses",
        new_callable=AsyncMock,
        return_value=[{"id": 1, "name": "Курс 1"}]
    )

    await process_choose_teacher_active_course(mock_callback, mock_callback)

    mock_find_courses.assert_called_once_with(123, mock_db_session)
    mock_callback.message.edit_text.assert_called_once_with("Выберите курс или сбростье его:")
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_choose_teacher_active_course_access_denied(mock_callback, mocker):
    """Тест выбора курса - нет доступа"""
    mocker.patch(
        "infra.telegram.routers.teacher_router.find_teachers_courses",
        side_effect=AccessDenied("Нет доступа")
    )

    await process_choose_teacher_active_course(mock_callback, mock_callback)

    mock_callback.message.edit_text.assert_called_once()
    assert "Нет доступа" in mock_callback.message.edit_text.call_args[0][0]
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_set_teacher_active_course_success(mock_callback, mock_state):
    """Тест установки активного курса"""
    mock_callback.data = "set_teacher_active_course:1"

    await process_set_teacher_active_course(mock_callback, mock_state)

    mock_state.update_data.assert_called_once_with(course_id=1)
    mock_callback.message.edit_text.assert_called_once_with(
        "Курс установлен",
        reply_markup=ANY
    )
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_set_teacher_active_course_reset(mock_callback, mock_state):
    """Тест сброса активного курса"""
    mock_callback.data = "set_teacher_active_course:0"

    await process_set_teacher_active_course(mock_callback, mock_state)

    mock_state.update_data.assert_called_once_with(course_id=None)
    mock_callback.message.edit_text.assert_called_once_with(
        "Курс сброшен",
        reply_markup=ANY
    )
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_process_previous_page_courses(mock_callback, mock_db_session, mocker):
    """Тест перехода на предыдущую страницу курсов"""
    mock_callback.data = "previous_paper_course_teacher:1"
    mock_find_courses = mocker.patch(
        "infra.telegram.routers.teacher_router.find_teachers_courses",
        new_callable=AsyncMock,
        return_value=[]
    )

    await process_previous_page(mock_callback, mock_callback)

    mock_find_courses.assert_called_once_with(123, mock_db_session)
    mock_callback.message.edit_text.assert_called_once()
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_process_next_page_courses(mock_callback, mock_db_session, mocker):
    """Тест перехода на следующую страницу курсов"""
    mock_callback.data = "next_paper_course_teacher:0"
    mock_find_courses = mocker.patch(
        "infra.telegram.routers.teacher_router.find_teachers_courses",
        new_callable=AsyncMock,
        return_value=[]
    )

    await process_next_page(mock_callback, mock_callback)

    mock_find_courses.assert_called_once_with(123, mock_db_session)
    mock_callback.message.edit_text.assert_called_once()
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_choose_teacher_active_assignment_with_course(mock_callback, mock_state, mock_db_session, mocker):
    """Тест выбора задания при наличии активного курса"""
    mock_state.get_data = AsyncMock(return_value={"course_id": 1})
    mock_find_assignments = mocker.patch(
        "infra.telegram.routers.teacher_router.find_assignments_by_course_id",
        new_callable=AsyncMock,
        return_value=[{"id": 1, "name": "Задание 1"}]
    )

    await process_choose_teacher_active_assignment(mock_callback, mock_state)

    mock_find_assignments.assert_called_once_with(1, mock_db_session)
    mock_callback.message.edit_text.assert_called_once_with("Выберите задание или сбростье его:")
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_choose_teacher_active_assignment_without_course(mock_callback, mock_state):
    """Тест выбора задания без активного курса"""
    mock_state.get_data = AsyncMock(return_value={"course_id": None})

    await process_choose_teacher_active_assignment(mock_callback, mock_state)

    mock_callback.message.edit_text.assert_called_once_with(
        "Чтобы выбрать активное задание, нужно выбрать активный курс."
    )
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_set_teacher_active_course_success(mock_callback, mock_state):
    """Тест установки активного задания"""
    mock_callback.data = "set_teacher_active_assignment:1"

    await process_set_teacher_active_assignment(mock_callback, mock_state)

    mock_state.update_data.assert_called_once_with(course_id=1)
    mock_callback.message.edit_text.assert_called_once_with(
        "Задание установлено",
        reply_markup=ANY
    )
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_set_teacher_active_course_reset(mock_callback, mock_state):
    """Тест сброса активного задания"""
    mock_callback.data = "set_teacher_active_assignment:0"

    await process_set_teacher_active_assignment(mock_callback, mock_state)

    mock_state.update_data.assert_called_once_with(course_id=None)
    mock_callback.message.edit_text.assert_called_once_with(
        "Задание сброшено",
        reply_markup=ANY
    )
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_process_previous_page_courses(mock_callback, mock_db_session, mocker):
    """Тест перехода на предыдущую страницу заданий"""
    mock_callback.data = "previous_paper_assignment_teacher:1"
    mock_find_assignments = mocker.patch(
        "infra.telegram.routers.teacher_router.find_assignments_by_course_id",
        new_callable=AsyncMock,
        return_value=[]
    )

    await process_previous_page(mock_callback, mock_callback)

    mock_find_assignments.assert_called_once_with(123, mock_db_session)
    mock_callback.message.edit_text.assert_called_once()
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_process_next_page_courses(mock_callback, mock_db_session, mocker):
    """Тест перехода на следующую страницу заданий"""
    mock_callback.data = "next_paper_assignment_teacher:0"
    mock_find_assignments = mocker.patch(
        "infra.telegram.routers.teacher_router.find_assignments_by_course_id",
        new_callable=AsyncMock,
        return_value=[]
    )

    await process_next_page(mock_callback, mock_callback)

    mock_find_assignments.assert_called_once_with(123, mock_db_session)
    mock_callback.message.edit_text.assert_called_once()
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_get_course_students_overview_success(mock_callback, mock_state, mock_db_session, mocker):
    """Тест получения сводки по студентам курса"""
    mock_state.get_data = AsyncMock(return_value={"course_id": 1})
    mock_get_overview = mocker.patch(
        "infra.telegram.routers.teacher_router.get_course_students_overview",
        new_callable=AsyncMock,
        return_value=[{"student": "Иван", "progress": "80%"}]
    )
    mock_table_to_text = mocker.patch(
        "infra.telegram.routers.teacher_router.table_to_text",
        new_callable=AsyncMock,
        return_value="Таблица данных"
    )

    await process_get_course_students_overview_teacher(mock_callback, mock_state)

    mock_get_overview.assert_called_once_with(123, 1, mock_db_session)
    mock_table_to_text.assert_called_once()
    mock_callback.message.edit_text.assert_called_once_with(
        "Таблица данных"
    )
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_get_course_students_overview_without_course(mock_callback, mock_state):
    """Тест получения сводки без активного курса"""
    mock_state.get_data = AsyncMock(return_value={"course_id": None})

    await process_get_course_students_overview_teacher(mock_callback, mock_state)

    mock_callback.message.edit_text.assert_called_once_with(
        "Для получения данных по курсу выберите активный курс",
        reply_markup=ANY
    )
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_get_assignment_students_status_success(mock_callback, mock_state, mock_db_session, mocker):
    """Тест получения статуса студентов по заданию"""
    mock_state.get_data = AsyncMock(return_value={"assignment_id": 1})
    mock_get_status = mocker.patch(
        "infra.telegram.routers.teacher_router.get_assignment_students_status",
        new_callable=AsyncMock,
        return_value=[{"student": "Иван", "status": "Сдано"}]
    )
    mock_table_to_text = mocker.patch(
        "infra.telegram.routers.teacher_router.table_to_text",
        new_callable=AsyncMock,
        return_value="Таблица статусов"
    )

    await process_get_assignment_students_status_teacher(mock_callback, mock_state)

    mock_get_status.assert_called_once_with(123, 1, mock_db_session)
    mock_callback.message.edit_text.assert_called_once()
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_get_classroom_users_without_bot_accounts_success(mock_callback, mock_state, mock_db_session, mocker):
    """Тест получения пользователей без аккаунтов бота"""
    mock_state.get_data = AsyncMock(return_value={"course_id": 1})
    mock_get_users = mocker.patch(
        "infra.telegram.routers.teacher_router.get_classroom_users_without_bot_accounts",
        new_callable=AsyncMock,
        return_value=["user1", "user2", "user3"]
    )

    await process_get_classroom_users_without_bot_accounts_teacher(mock_callback, mock_state)

    mock_get_users.assert_called_once_with(123, 1, mock_db_session)
    mock_callback.message.edit_text.assert_called_once()
    text = mock_callback.message.edit_text.call_args[0][0]
    assert "user1" in text
    assert "user2" in text
    assert "user3" in text
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_add_course_assistant_teacher_first_with_course(mock_callback, mock_state):
    """Тест начала добавления ассистента с активным курсом"""
    mock_state.get_data = AsyncMock(return_value={"course_id": 1})

    await process_add_course_assistant_teacher_first(mock_callback, mock_state)

    mock_state.set_state.assert_called_once_with(ANY)
    mock_callback.message.edit_text.assert_called_once_with(
        "Введите ник ассистента в виде @username или username:"
    )
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_add_course_assistant_teacher_first_without_course(mock_callback, mock_state):
    """Тест начала добавления ассистента без активного курса"""
    mock_state.get_data = AsyncMock(return_value={"course_id": None})

    await process_add_course_assistant_teacher_first(mock_callback, mock_state)

    mock_callback.message.edit_text.assert_called_once_with(
        "Для добавления ассистента выберите активный курс"
    )
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_add_course_assistant_teacher_second_success(mock_message, mock_state, mock_db_session, mocker):
    """Тест добавления ассистента"""
    mock_message.text = "assistant_user"
    mock_state.get_data = AsyncMock(return_value={"course_id": 1})
    mock_add_assistant = mocker.patch(
        "infra.telegram.routers.teacher_router.add_course_assistant",
        new_callable=AsyncMock
    )

    await process_add_course_assistant_teacher_second(mock_message, mock_state)

    mock_add_assistant.assert_called_once_with(123, 1, "assistant_user", mock_db_session)
    mock_message.answer.assert_called_once_with(
        "Ассистент успешно добавлен!",
        reply_markup=ANY
    )
    mock_state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_create_course_announcement_teacher_second_success(mock_message, mock_state, mock_db_session, mocker):
    """Тест создания объявления на курсе"""
    mock_message.text = "Важное объявление!"
    mock_state.get_data = AsyncMock(return_value={"course_id": 1})
    mock_create_announcement = mocker.patch(
        "infra.telegram.routers.teacher_router.create_course_announcement",
        new_callable=AsyncMock,
        return_value=[111, 222, 333]
    )

    await process_create_course_announcement_teacher_second(mock_message, mock_state)

    mock_create_announcement.assert_called_once_with(123, 1, mock_db_session)
    assert mock_message.bot.send_message.call_count == 3
    mock_message.answer.assert_called_once_with(
        "Уведомление успешно создано!"
    )
    mock_state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_select_manual_check_assignment_success(mock_callback, mock_state, mock_db_session, mocker):
    """Тест установки ручной проверки задания"""
    mock_state.get_data = AsyncMock(return_value={"assignment_id": 1})
    mock_select_check = mocker.patch(
        "infra.telegram.routers.teacher_router.select_manual_check_assignment",
        new_callable=AsyncMock
    )

    await process_select_manual_check_assignment_teacher(mock_callback, mock_state)

    mock_select_check.assert_called_once_with(1, mock_db_session)
    mock_callback.message.edit_text.assert_called_once_with(
        "Ручная проверка установлена."
    )
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_delete_manual_check_assignment_success(mock_callback, mock_state, mock_db_session, mocker):
    """Тест удаления ручной проверки задания"""
    mock_state.get_data = AsyncMock(return_value={"assignment_id": 1})
    mock_delete_check = mocker.patch(
        "infra.telegram.routers.teacher_router.delete_manual_check_assignment",
        new_callable=AsyncMock
    )

    await process_delete_manual_check_assignment_teacher(mock_callback, mock_state)

    mock_delete_check.assert_called_once_with(1, mock_db_session)
    mock_callback.message.edit_text.assert_called_once_with(
        "Автоматическая проверка установлена."
    )
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("handler", [
    process_choose_teacher_active_course,
    process_set_teacher_active_course,
    process_choose_teacher_active_assignment,
    process_get_course_students_overview_teacher,
    process_get_assignment_students_status_teacher,
    process_get_classroom_users_without_bot_accounts_teacher,
])
async def test_handlers_access_denied(handler, mock_callback, mock_state, mocker):
    """Общий тест для обработки AccessDenied во всех обработчиках"""
    for func_name in [
        "find_teachers_courses",
        "get_course_students_overview",
        "get_assignment_students_status",
        "get_classroom_users_without_bot_accounts",
    ]:
        try:
            mocker.patch(
                f"infra.telegram.routers.teacher_router.{func_name}",
                side_effect=AccessDenied("Доступ запрещен")
            )
            break
        except:
            continue
    if handler in [process_choose_teacher_active_assignment,
                   process_get_course_students_overview_teacher,
                   process_get_assignment_students_status_teacher,
                   process_get_classroom_users_without_bot_accounts_teacher]:
        mock_state.get_data = AsyncMock(return_value={"course_id": 1, "assignment_id": 1})

    if handler == process_set_teacher_active_course:
        mock_callback.data = "set_teacher_active_course:1"

    await handler(mock_callback, mock_state)

    mock_callback.message.edit_text.assert_called_once()
    assert "Доступ запрещен" in mock_callback.message.edit_text.call_args[0][0]
    mock_callback.answer.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("handler", [
    process_add_course_assistant_teacher_second,
    process_remove_course_assistant_teacher_second,
    process_create_course_announcement_teacher_second,
])
async def test_message_handlers_value_error(handler, mock_message, mock_state, mocker):
    """Тест обработки ValueError в обработчиках сообщений"""
    mock_message.text = "test_input"
    mock_state.get_data = AsyncMock(return_value={"course_id": 1})

    func_name = "add_course_assistant" if "add" in handler.__name__ else \
        "remove_course_assistant" if "remove" in handler.__name__ else \
            "create_course_announcement"

    mocker.patch(
        f"infra.telegram.routers.teacher_router.{func_name}",
        side_effect=ValueError("Некорректные данные")
    )

    await handler(mock_message, mock_state)

    mock_message.answer.assert_called_once()
    assert "Некорректные данные" in mock_message.answer.call_args[0][0]
    mock_state.clear.assert_called_once()