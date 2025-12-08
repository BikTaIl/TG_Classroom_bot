import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
from dotenv import load_dotenv
from commands.common_commands import complete_github_link

load_dotenv()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

app = FastAPI()

@app.get("/oauth/github/callback")
async def github_callback(request: Request):
    """
    Callback endpoint для GitHub OAuth.
    GitHub пришлет ?code=XXX&state=YYY
    """
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    telegram_id = int(state)

    # Автоматически вызываем твою бизнес-функцию
    github_user = await complete_github_link(
        telegram_id=telegram_id,
        code=code,
        state=state
    )
    username = github_user["login"]
    print(f"inside gihub callback: {username}")
    return HTMLResponse(f"<h3>GitHub успешно привязан!</h3><pre>{username}</pre>")

    # Обменяем code на access_token
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "state": state
            }
        )
        resp.raise_for_status()
        token_data = resp.json()

    access_token = token_data.get("access_token")
    if not access_token:
        return HTMLResponse(f"<h3>Ошибка при получении токена</h3><pre>{token_data}</pre>")

    # Здесь можно сразу сохранять токен в БД, связав с пользователем Telegram
    return HTMLResponse(f"<h3>GitHub успешно привязан!</h3><pre>{token_data}</pre>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
