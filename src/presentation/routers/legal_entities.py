from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.application.use_cases.legal_entity import (
    DeleteLegalEntity,
    GetAllLegalEntities,
    GetLegalEntity,
    SaveLegalEntity,
)
from src.domain.entities.legal_entity import ContractType, LegalEntity
from src.infrastructure.database.session import get_db
from src.infrastructure.repositories.legal_entity_repository import SQLLegalEntityRepository

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parents[1] / "templates")


def _repo(db: Session = Depends(get_db)) -> SQLLegalEntityRepository:
    return SQLLegalEntityRepository(db)


@router.get("/", response_class=HTMLResponse)
def index(request: Request, search: str = "", db: Session = Depends(get_db)):
    entities = GetAllLegalEntities(_repo(db)).execute()
    if search:
        entities = [e for e in entities if search.lower() in e.name.lower()]
    return templates.TemplateResponse(
        "legal_entities/list.html",
        {"request": request, "entities": entities, "search": search},
    )


@router.get("/legal-entities/new", response_class=HTMLResponse)
def new_form(request: Request):
    return templates.TemplateResponse(
        "legal_entities/form.html",
        {"request": request, "entity": None, "contract_types": list(ContractType)},
    )


@router.post("/legal-entities/new")
def create(
    name: str = Form(...),
    contract_type: str = Form(...),
    contract_number: int = Form(0),
    code: int | None = Form(None),
    db: Session = Depends(get_db),
):
    entity = LegalEntity(
        name=name,
        contract_type=ContractType(contract_type),
        contract_number=contract_number,
        code=code,
    )
    saved = SaveLegalEntity(_repo(db)).execute(entity)
    return RedirectResponse(f"/legal-entities/{saved.id}", status_code=303)


@router.get("/legal-entities/{entity_id}", response_class=HTMLResponse)
def detail(entity_id: int, request: Request, db: Session = Depends(get_db)):
    entity = GetLegalEntity(_repo(db)).execute(entity_id)
    if entity is None:
        return RedirectResponse("/")
    from src.infrastructure.repositories.object_repository import SQLObjectRepository
    from src.application.use_cases.guarded_object import GetObjectsByLegalEntity

    objects = GetObjectsByLegalEntity(SQLObjectRepository(db)).execute(entity_id)
    return templates.TemplateResponse(
        "legal_entities/detail.html",
        {
            "request": request,
            "entity": entity,
            "objects": objects,
            "contract_types": list(ContractType),
        },
    )


@router.post("/legal-entities/{entity_id}/edit")
def edit(
    entity_id: int,
    name: str = Form(...),
    contract_type: str = Form(...),
    contract_number: int = Form(0),
    code: int | None = Form(None),
    db: Session = Depends(get_db),
):
    entity = LegalEntity(
        id=entity_id,
        name=name,
        contract_type=ContractType(contract_type),
        contract_number=contract_number,
        code=code,
    )
    SaveLegalEntity(_repo(db)).execute(entity)
    return RedirectResponse(f"/legal-entities/{entity_id}", status_code=303)


@router.post("/legal-entities/{entity_id}/delete")
def delete(entity_id: int, db: Session = Depends(get_db)):
    DeleteLegalEntity(_repo(db)).execute(entity_id)
    return RedirectResponse("/", status_code=303)
