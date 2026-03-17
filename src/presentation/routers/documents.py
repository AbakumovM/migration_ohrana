"""Роутер для генерации PDF-документов по объекту."""

from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.application.use_cases.guarded_object import GetObject, GetObjectServices
from src.infrastructure.database.models import OrgSettingsModel
from src.infrastructure.database.session import get_db
from src.infrastructure.repositories.legal_entity_repository import SQLLegalEntityRepository
from src.infrastructure.repositories.object_repository import SQLObjectRepository

router = APIRouter(prefix="/objects/{object_id}/documents")
templates = Jinja2Templates(directory=Path(__file__).parents[1] / "templates")


def _get_context(object_id: int, db: Session) -> dict:
    """Собирает контекст для шаблона документа: объект, виды охраны, юр. лицо, реквизиты."""
    obj_repo = SQLObjectRepository(db)
    obj = GetObject(obj_repo).execute(object_id)
    services = GetObjectServices(obj_repo).execute(object_id)
    legal_entity = SQLLegalEntityRepository(db).get_by_id(obj.legal_entity_id) if obj else None
    settings = db.query(OrgSettingsModel).first()
    return {
        "obj": obj,
        "services": services,
        "legal_entity": legal_entity,
        "settings": settings,
    }


@router.get("/{doc_type}")
def generate(object_id: int, doc_type: str, db: Session = Depends(get_db)):
    """Генерирует PDF-документ указанного типа для объекта охраны."""
    from weasyprint import HTML

    context = _get_context(object_id, db)
    template_name = f"documents/{doc_type}.html"
    html_content = templates.get_template(template_name).render(context)
    pdf = HTML(string=html_content).write_pdf()
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{doc_type}_{object_id}.pdf"'},
    )
