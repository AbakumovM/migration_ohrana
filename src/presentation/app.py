from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.infrastructure.database.models import Base
from src.infrastructure.database.session import engine
from src.presentation.auth import SECRET_KEY
from src.presentation.routers import archive, documents, legal_entities, objects, settings
from src.presentation.routers import auth as auth_router

Base.metadata.create_all(engine)

app = FastAPI(title="Охрана — управление объектами")

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AuthMiddleware(BaseHTTPMiddleware):
    """Перенаправляет неавторизованных пользователей на /login."""

    EXEMPT = {"/login"}

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        path = request.url.path
        if path not in self.EXEMPT and not path.startswith("/static"):
            if not request.session.get("authenticated"):
                return RedirectResponse("/login")
        return await call_next(request)


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
