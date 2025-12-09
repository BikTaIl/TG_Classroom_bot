import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from commands.common_commands import complete_github_link
from uvicorn import Config, Server
import asyncio

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

    github_user = await complete_github_link(
        telegram_id=telegram_id,
        code=code,
        state=state
    )
    username = github_user["login"]
    print(f"inside gihub callback: {username}")
    return HTMLResponse(f"<h3>GitHub успешно привязан!</h3><pre>{username}</pre>")

async def start_fastapi():
    config = Config("auth.auth_service:app", host="127.0.0.1", port=8000, loop="asyncio")
    server = Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(start_fastapi())
