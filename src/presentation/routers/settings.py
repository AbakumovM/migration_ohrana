"""Роутер для управления реквизитами организации."""

from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.application.use_cases.org_settings import GetOrgSettings, SaveOrgSettings
from src.domain.entities.org_settings import OrgSettings
from src.infrastructure.database.session import get_db
from src.infrastructure.repositories.org_settings_repository import SQLOrgSettingsRepository

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parents[1] / "templates")


def _repo(db: Session) -> SQLOrgSettingsRepository:
    return SQLOrgSettingsRepository(db)


@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, saved: bool = False, db: Session = Depends(get_db)):
    settings = GetOrgSettings(_repo(db)).execute()
    return templates.TemplateResponse(
        "settings/index.html",
        {"request": request, "settings": settings, "saved": saved},
    )


@router.post("/settings")
def settings_save(
    chief_name: str = Form(""),
    chief_title: str = Form(""),
    org_name: str = Form(""),
    db: Session = Depends(get_db),
):
    SaveOrgSettings(_repo(db)).execute(
        OrgSettings(chief_name=chief_name, chief_title=chief_title, org_name=org_name)
    )
    return RedirectResponse("/settings?saved=1", status_code=303)
