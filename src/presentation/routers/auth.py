"""Роутер авторизации: страница входа и выход."""

from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.presentation.auth import verify_credentials

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parents[1] / "templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    """Страница входа. Если уже авторизован — редирект на главную."""
    if request.session.get("authenticated"):
        return RedirectResponse("/", status_code=302)  # type: ignore[return-value]
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
) -> HTMLResponse:
    """Обработка формы входа."""
    if verify_credentials(username, password):
        request.session["authenticated"] = True
        return RedirectResponse("/", status_code=302)  # type: ignore[return-value]
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Неверный логин или пароль"},
    )


@router.get("/logout")
async def logout(request: Request) -> RedirectResponse:
    """Выход из системы."""
    request.session.clear()
    return RedirectResponse("/login", status_code=302)
