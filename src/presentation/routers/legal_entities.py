"""Роутер для работы с юридическими лицами."""

from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.application.use_cases.guarded_object import GetObjectsByLegalEntity
from src.application.use_cases.legal_entity import (
    DeleteLegalEntity,
    GetAllLegalEntities,
    GetLegalEntity,
    SaveLegalEntity,
    SearchLegalEntities,
)
from src.domain.entities.legal_entity import ContractType, LegalEntity
from src.infrastructure.database.session import get_db
from src.infrastructure.repositories.legal_entity_repository import SQLLegalEntityRepository
from src.infrastructure.repositories.object_repository import SQLObjectRepository

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parents[1] / "templates")


def _le_repo(db: Session) -> SQLLegalEntityRepository:
    return SQLLegalEntityRepository(db)


def _obj_repo(db: Session) -> SQLObjectRepository:
    return SQLObjectRepository(db)


@router.get("/", response_class=HTMLResponse)
def index(request: Request, search: str = "", db: Session = Depends(get_db)):
    repo = _le_repo(db)
    entities = SearchLegalEntities(repo).execute(search) if search else GetAllLegalEntities(repo).execute()
    object_counts = _obj_repo(db).count_active_by_legal_entities()
    return templates.TemplateResponse(
        "legal_entities/list.html",
        {"request": request, "entities": entities, "search": search, "object_counts": object_counts},
    )


@router.get("/legal-entities/new", response_class=HTMLResponse)
def new_form(request: Request, db: Session = Depends(get_db)):
    next_number = _le_repo(db).get_next_contract_number()
    return templates.TemplateResponse(
        "legal_entities/form.html",
        {"request": request, "entity": None, "contract_types": list(ContractType), "next_number": next_number},
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
    saved = SaveLegalEntity(_le_repo(db)).execute(entity)
    return RedirectResponse(f"/legal-entities/{saved.id}", status_code=303)


@router.get("/legal-entities/{entity_id}", response_class=HTMLResponse)
def detail(entity_id: int, request: Request, db: Session = Depends(get_db)):
    entity = GetLegalEntity(_le_repo(db)).execute(entity_id)
    if entity is None:
        return RedirectResponse("/")
    obj_repo = _obj_repo(db)
    objects = GetObjectsByLegalEntity(obj_repo).execute(entity_id)
    archived = obj_repo.get_archived(entity_id)
    # Виды охраны для каждого объекта: {object_id: [service_type.value, ...]}
    service_types_map: dict[int, list[str]] = {}
    for obj in objects + archived:
        if obj.id is not None:
            service_types_map[obj.id] = [
                s.service_type.value for s in obj_repo.get_services(obj.id)
            ]
    return templates.TemplateResponse(
        "legal_entities/detail.html",
        {
            "request": request,
            "entity": entity,
            "objects": objects,
            "archived": archived,
            "service_types_map": service_types_map,
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
    SaveLegalEntity(_le_repo(db)).execute(entity)
    return RedirectResponse(f"/legal-entities/{entity_id}", status_code=303)


@router.post("/legal-entities/{entity_id}/delete")
def delete(entity_id: int, db: Session = Depends(get_db)):
    DeleteLegalEntity(_le_repo(db)).execute(entity_id)
    return RedirectResponse("/", status_code=303)
