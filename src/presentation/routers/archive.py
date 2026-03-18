"""Роутер раздела «Архив» — список всех архивных объектов с возможностью восстановления."""

from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.infrastructure.database.session import get_db
from src.infrastructure.repositories.legal_entity_repository import SQLLegalEntityRepository
from src.infrastructure.repositories.object_repository import SQLObjectRepository

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parents[1] / "templates")


@router.get("/archive", response_class=HTMLResponse)
def archive_index(request: Request, db: Session = Depends(get_db)):
    """Отображает список всех архивных объектов охраны."""
    obj_repo = SQLObjectRepository(db)
    le_repo = SQLLegalEntityRepository(db)

    archived = obj_repo.get_all_archived()
    entities = {e.id: e for e in le_repo.get_all()}
    services_map = {obj.id: obj_repo.get_services(obj.id) for obj in archived}

    return templates.TemplateResponse(
        "archive/index.html",
        {
            "request": request,
            "archived": archived,
            "entities": entities,
            "services_map": services_map,
        },
    )
