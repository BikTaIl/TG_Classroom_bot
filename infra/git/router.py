from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from infra.git.github_service import complete_github_link
from uvicorn import Config, Server
import asyncio
from infra.db import AsyncSessionLocal

app = FastAPI()

@app.get("/oauth/github/callback")
async def github_callback(request: Request):
    """
    Callback endpoint для GitHub OAuth.
    GitHub пришлет ?code=XXX&state=YYY
    """
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")

    async with AsyncSessionLocal() as session:
        try:
            github_user = await complete_github_link(
                code=code,
                state=state,
                session=session
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid or expired state")

    username = github_user["login"]

    return HTMLResponse(
        f"<h3>GitHub успешно привязан!</h3>"
        f"<p>GitHub: {username}</p>"
    )

async def start_fastapi():
    config = Config("infra.git.router:app", host="127.0.0.1", port=8000, loop="asyncio")
    server = Server(config)
    print('Роутер запущен')
    await server.serve()

if __name__ == "__main__":
    asyncio.run(start_fastapi())
