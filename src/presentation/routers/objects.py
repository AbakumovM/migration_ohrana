"""Роутер для работы с охраняемыми объектами, видами охраны и расписанием."""

from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.application.use_cases.guarded_object import (
    ArchiveObject,
    DeleteObject,
    DeleteObjectService,
    GetObject,
    GetObjectServices,
    SaveObject,
    SaveObjectService,
    UnarchiveObject,
)
from src.domain.entities.guarded_object import GuardedObject
from src.domain.entities.object_service import GuardSchedule, ObjectService, ServiceType
from src.infrastructure.database.session import get_db
from src.infrastructure.repositories.object_repository import SQLObjectRepository

router = APIRouter(prefix="/objects")
templates = Jinja2Templates(directory=Path(__file__).parents[1] / "templates")


def _repo(db: Session = Depends(get_db)) -> SQLObjectRepository:
    return SQLObjectRepository(db)


@router.get("/new", response_class=HTMLResponse)
def new_form(request: Request, legal_entity_id: int):
    return templates.TemplateResponse(
        "objects/form.html",
        {"request": request, "obj": None, "legal_entity_id": legal_entity_id},
    )


@router.post("/new")
def create(
    legal_entity_id: int = Form(...),
    name: str = Form(...),
    town: str = Form(""),
    street: str = Form(""),
    phone: str = Form(""),
    signatory: str = Form(""),
    accepted_date: str = Form(""),
    db: Session = Depends(get_db),
):
    obj = GuardedObject(
        legal_entity_id=legal_entity_id,
        name=name,
        town=town,
        street=street,
        phone=phone,
        signatory=signatory,
        accepted_date=date.fromisoformat(accepted_date) if accepted_date else None,
    )
    saved = SaveObject(_repo(db)).execute(obj)
    return RedirectResponse(f"/objects/{saved.id}", status_code=303)


@router.get("/{object_id}", response_class=HTMLResponse)
def detail(object_id: int, request: Request, db: Session = Depends(get_db)):
    repo = _repo(db)
    obj = GetObject(repo).execute(object_id)
    if obj is None:
        return RedirectResponse("/")
    services = GetObjectServices(repo).execute(object_id)
    return templates.TemplateResponse(
        "objects/detail.html",
        {
            "request": request,
            "obj": obj,
            "services": services,
            "service_types": list(ServiceType),
        },
    )


@router.post("/{object_id}/edit")
def edit(
    object_id: int,
    legal_entity_id: int = Form(...),
    name: str = Form(...),
    town: str = Form(""),
    street: str = Form(""),
    phone: str = Form(""),
    signatory: str = Form(""),
    accepted_date: str = Form(""),
    db: Session = Depends(get_db),
):
    obj = GuardedObject(
        id=object_id,
        legal_entity_id=legal_entity_id,
        name=name,
        town=town,
        street=street,
        phone=phone,
        signatory=signatory,
        accepted_date=date.fromisoformat(accepted_date) if accepted_date else None,
    )
    SaveObject(_repo(db)).execute(obj)
    return RedirectResponse(f"/objects/{object_id}", status_code=303)


@router.post("/{object_id}/archive")
def archive(object_id: int, db: Session = Depends(get_db)):
    repo = _repo(db)
    obj = GetObject(repo).execute(object_id)
    legal_entity_id = obj.legal_entity_id if obj else None
    ArchiveObject(repo).execute(object_id)
    return RedirectResponse(
        f"/legal-entities/{legal_entity_id}" if legal_entity_id else "/", status_code=303
    )


@router.post("/{object_id}/unarchive")
def unarchive(object_id: int, db: Session = Depends(get_db)):
    UnarchiveObject(_repo(db)).execute(object_id)
    return RedirectResponse("/archive", status_code=303)


@router.post("/{object_id}/delete")
def delete(object_id: int, db: Session = Depends(get_db)):
    repo = _repo(db)
    obj = GetObject(repo).execute(object_id)
    legal_entity_id = obj.legal_entity_id if obj else None
    DeleteObject(repo).execute(object_id)
    return RedirectResponse(
        f"/legal-entities/{legal_entity_id}" if legal_entity_id else "/", status_code=303
    )


@router.post("/{object_id}/services/add")
def add_service(
    object_id: int,
    service_type: str = Form(...),
    date_from: str = Form(""),
    date_to: str = Form(""),
    tariff: float = Form(0.0),
    period: int = Form(12),
    db: Session = Depends(get_db),
):
    service = ObjectService(
        object_id=object_id,
        service_type=ServiceType(service_type),
        date_from=date.fromisoformat(date_from) if date_from else None,
        date_to=date.fromisoformat(date_to) if date_to else None,
        tariff=tariff,
        period=period,
    )
    SaveObjectService(_repo(db)).execute(service)
    return RedirectResponse(f"/objects/{object_id}", status_code=303)


@router.post("/{object_id}/services/{service_id}/delete")
def delete_service(object_id: int, service_id: int, db: Session = Depends(get_db)):
    DeleteObjectService(_repo(db)).execute(service_id)
    return RedirectResponse(f"/objects/{object_id}", status_code=303)


@router.get("/{object_id}/services/{service_id}/schedule", response_class=HTMLResponse)
def schedule_form(object_id: int, service_id: int, request: Request, db: Session = Depends(get_db)):
    services = GetObjectServices(_repo(db)).execute(object_id)
    service = next((s for s in services if s.id == service_id), None)
    if service is None:
        return RedirectResponse(f"/objects/{object_id}")
    return templates.TemplateResponse(
        "objects/schedule.html",
        {"request": request, "service": service, "object_id": object_id},
    )


@router.post("/{object_id}/services/{service_id}/schedule")
def save_schedule(
    object_id: int,
    service_id: int,
    work_start: str = Form("08:00"),
    work_end: str = Form("18:00"),
    days_off: str = Form("суб.,вск.,праз"),
    workday_from: str = Form("18:00"),
    workday_to: str = Form("08:00"),
    workday_count: int = Form(0),
    preholiday_from: str = Form("18:00"),
    preholiday_to: str = Form("08:00"),
    preholiday_count: int = Form(0),
    holiday_from: str = Form("00:00"),
    holiday_to: str = Form("24:00"),
    holiday_count: int = Form(0),
    tariff: float = Form(0.0),
    period: int = Form(12),
    date_from: str = Form(""),
    date_to: str = Form(""),
    db: Session = Depends(get_db),
):
    repo = _repo(db)
    services = GetObjectServices(repo).execute(object_id)
    service = next((s for s in services if s.id == service_id), None)
    if service is None:
        return RedirectResponse(f"/objects/{object_id}")

    service.tariff = tariff
    service.period = period
    service.date_from = date.fromisoformat(date_from) if date_from else service.date_from
    service.date_to = date.fromisoformat(date_to) if date_to else service.date_to
    service.schedule = GuardSchedule(
        id=service.schedule.id if service.schedule else None,
        work_start=work_start,
        work_end=work_end,
        days_off=days_off,
        workday_from=workday_from,
        workday_to=workday_to,
        workday_count=workday_count,
        preholiday_from=preholiday_from,
        preholiday_to=preholiday_to,
        preholiday_count=preholiday_count,
        holiday_from=holiday_from,
        holiday_to=holiday_to,
        holiday_count=holiday_count,
    )
    SaveObjectService(repo).execute(service)
    return RedirectResponse(f"/objects/{object_id}", status_code=303)
