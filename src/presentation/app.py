from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

from src.infrastructure.database.models import Base
from src.infrastructure.database.session import engine
from src.presentation.auth import SECRET_KEY
from src.presentation.routers import archive, documents, legal_entities, objects, settings
from src.presentation.routers import auth as auth_router

Base.metadata.create_all(engine)

app = FastAPI(title="Охрана — управление объектами")

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AuthMiddleware:
    """Перенаправляет неавторизованных пользователей на /login.

    Чистый ASGI-middleware — не буферизует тело запроса,
    поэтому корректно работает с form data.
    """

    EXEMPT = {"/login"}

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> Any:
        if scope["type"] == "http":
            path: str = scope["path"]
            if path not in self.EXEMPT and not path.startswith("/static"):
                session: dict = scope.get("session", {})
                if not session.get("authenticated"):
                    response = RedirectResponse("/login")
                    await response(scope, receive, send)
                    return
        await self.app(scope, receive, send)


# Порядок важен: SessionMiddleware добавляется последним → выполняется первым
app.add_middleware(AuthMiddleware)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.include_router(auth_router.router)
app.include_router(legal_entities.router)
app.include_router(objects.router)
app.include_router(documents.router)
app.include_router(archive.router)
app.include_router(settings.router)

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
