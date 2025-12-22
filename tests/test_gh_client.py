import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from models.gh_client import GitHubClassroomClient


@pytest.fixture
def gh_client():
    return GitHubClassroomClient(token="test_token")


@pytest.mark.asyncio
async def test_get_courses(gh_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "name": "Course 1"},
        {"id": 2, "name": "Course 2"},
    ]
    mock_response.raise_for_status.return_value = None

    with patch("httpx.Client") as mock_client:
        instance = mock_client.return_value.__enter__.return_value
        instance.get.return_value = mock_response

        courses = await gh_client.get_courses()

    assert len(courses) == 2
    assert courses[0]["name"] == "Course 1"


@pytest.mark.asyncio
async def test_get_course_details(gh_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1,
        "name": "Course 1",
        "organization": "Org"
    }
    mock_response.raise_for_status.return_value = None

    with patch("httpx.AsyncClient") as mock_client:
        instance = mock_client.return_value.__aenter__.return_value
        instance.get = AsyncMock(return_value=mock_response)

        details = await gh_client.get_course_details(1)

    assert details["id"] == 1
    assert details["organization"] == "Org"


@pytest.mark.asyncio
async def test_get_assignments(gh_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 10, "title": "Assignment 1"},
        {"id": 11, "title": "Assignment 2"},
    ]
    mock_response.raise_for_status.return_value = None

    with patch("httpx.Client") as mock_client:
        instance = mock_client.return_value.__enter__.return_value
        instance.get.return_value = mock_response

        assignments = await gh_client.get_assignments(123)

    assert len(assignments) == 2
    assert assignments[0]["title"] == "Assignment 1"


@pytest.mark.asyncio
async def test_get_last_commit_time_success(gh_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "commit": {
                "author": {
                    "date": "2024-01-01T12:00:00Z"
                }
            }
        }
    ]

    with patch("httpx.AsyncClient") as mock_client:
        instance = mock_client.return_value.__aenter__.return_value
        instance.get = AsyncMock(return_value=mock_response)

        date = await gh_client.get_last_commit_time("owner/repo")

    assert date == "2024-01-01T12:00:00Z"


@pytest.mark.asyncio
async def test_get_last_commit_time_failed(gh_client):
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("httpx.AsyncClient") as mock_client:
        instance = mock_client.return_value.__aenter__.return_value
        instance.get = AsyncMock(return_value=mock_response)

        date = await gh_client.get_last_commit_time("owner/repo")

    assert date is None


@pytest.mark.asyncio
async def test_get_submissions(gh_client):
    submissions_response = MagicMock()
    submissions_response.status_code = 200
    submissions_response.json.return_value = [
        {"id": 1, "repository": {"full_name": "owner/repo"}}
    ]
    submissions_response.raise_for_status.return_value = None

    with patch("httpx.Client") as mock_client, \
         patch.object(
             gh_client,
             "get_last_commit_time",
             new=AsyncMock(return_value="2024-01-01T12:00:00Z")
         ):

        instance = mock_client.return_value.__enter__.return_value
        instance.get.return_value = submissions_response

        result = await gh_client.get_submissions(10)

    assert result[0]["last_commit_at"] == "2024-01-01T12:00:00Z"


@pytest.mark.asyncio
async def test_get_submissions_no_repository(gh_client):
    submissions_response = MagicMock()
    submissions_response.status_code = 200
    submissions_response.json.return_value = [
        {"id": 1}
    ]
    submissions_response.raise_for_status.return_value = None

    with patch("httpx.Client") as mock_client:
        instance = mock_client.return_value.__enter__.return_value
        instance.get.return_value = submissions_response

        result = await gh_client.get_submissions(10)

    assert result[0]["last_commit_at"] is None


@pytest.mark.asyncio
async def test_test_connection_success(gh_client):
    with patch.object(gh_client, "get_courses", new=AsyncMock(return_value=[])):
        assert await gh_client.test_connection() is True


@pytest.mark.asyncio
async def test_test_connection_failure(gh_client):
    with patch.object(gh_client, "get_courses", new=AsyncMock(side_effect=Exception)):
        assert await gh_client.test_connection() is False