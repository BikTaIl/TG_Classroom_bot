from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from infra.git.github_service import complete_github_link
from uvicorn import Config, Server
import asyncio
from infra.db import AsyncSessionLocal
import time
from models.db import GitLogs

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response

    except Exception as exc:
        raise

    finally:
        process_time = time.time() - start_time
        client_ip = request.client.host if request.client else None

        try:
            async with AsyncSessionLocal() as session:
                session.add(
                    GitLogs(
                        log_status=status_code,
                        log_message=f"client_ip: {client_ip}, {request.method} {request.url.path} ({process_time:.3f}s)",
                    )
                )
                await session.commit()
        except Exception as e:
            print("LOGGING FAILED:", e)


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
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    username = github_user["login"]

    return HTMLResponse(
        f"<h3>GitHub успешно привязан!</h3>"
        f"<p>GitHub: {username}</p>"
    )

async def start_fastapi():
    config = Config("infra.git.router:app", host="127.0.0.1", port=8000, loop="asyncio")
    server = Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(start_fastapi())
