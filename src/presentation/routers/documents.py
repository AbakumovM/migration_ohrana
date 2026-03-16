"""Роутер для генерации PDF-документов по объекту."""

from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.application.use_cases.guarded_object import GetObject, GetObjectServices
from src.infrastructure.database.models import LegalEntityModel, OrgSettingsModel
from src.infrastructure.database.session import get_db
from src.infrastructure.repositories.object_repository import SQLObjectRepository

router = APIRouter(prefix="/objects/{object_id}/documents")
templates = Jinja2Templates(directory=Path(__file__).parents[1] / "templates")


def _get_context(object_id: int, db: Session) -> dict:
    repo = SQLObjectRepository(db)
    obj = GetObject(repo).execute(object_id)
    services = GetObjectServices(repo).execute(object_id)
    le = db.get(LegalEntityModel, obj.legal_entity_id) if obj else None
    settings = db.query(OrgSettingsModel).first()
    return {
        "obj": obj,
        "services": services,
        "legal_entity": le,
        "settings": settings,
    }


@router.get("/{doc_type}")
def generate(object_id: int, doc_type: str, db: Session = Depends(get_db)):
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
