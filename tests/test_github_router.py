import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from infra.git.router import app


client = TestClient(app)


@pytest.mark.asyncio
async def test_github_callback_success():
    fake_user = {"login": "testuser"}

    with patch(
        "infra.git.router.complete_github_link",
        new=AsyncMock(return_value=fake_user)
    ):
        with patch("infra.git.router.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.begin.return_value.__aenter__.return_value = None
            mock_session_local.return_value.__aenter__.return_value = mock_session

            response = client.get(
                "/oauth/github/callback?code=123&state=abc"
            )

    assert response.status_code == 200
    assert "GitHub успешно привязан" in response.text
    assert "testuser" in response.text


def test_github_callback_missing_params():
    response = client.get("/oauth/github/callback")
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing code or state"


@pytest.mark.asyncio
async def test_github_callback_invalid_state():
    with patch(
        "infra.git.router.complete_github_link",
        new=AsyncMock(side_effect=ValueError("Invalid or expired state"))
    ):
        with patch("infra.git.router.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.begin.return_value.__aenter__.return_value = None
            mock_session_local.return_value.__aenter__.return_value = mock_session

            response = client.get(
                "/oauth/github/callback?code=123&state=bad"
            )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired state"


def test_log_requests_writes_log():
    with patch("infra.git.router.AsyncSessionLocal") as mock_session_local:
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        mock_session_local.return_value.__aenter__.return_value = mock_session

        with patch(
            "infra.git.router.complete_github_link",
            new=AsyncMock(return_value={"login": "testuser"})
        ):
            response = client.get(
                "/oauth/github/callback?code=1&state=2"
            )

    assert response.status_code == 200
