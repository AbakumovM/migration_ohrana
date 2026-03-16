from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.application.use_cases.inspection import (
    DeleteInspection,
    GetInspectionsByObject,
    SaveInspection,
)
from src.domain.entities.inspection import Inspection
from src.infrastructure.database.session import get_db
from src.infrastructure.repositories.inspection_repository import SQLInspectionRepository

router = APIRouter(prefix="/objects/{object_id}/inspections")
templates = Jinja2Templates(directory=Path(__file__).parents[1] / "templates")


def _repo(db: Session = Depends(get_db)) -> SQLInspectionRepository:
    return SQLInspectionRepository(db)


@router.get("/", response_class=HTMLResponse)
def list_inspections(object_id: int, request: Request, db: Session = Depends(get_db)):
    inspections = GetInspectionsByObject(_repo(db)).execute(object_id)
    return templates.TemplateResponse(
        "objects/inspections.html",
        {"request": request, "inspections": inspections, "object_id": object_id},
    )


@router.post("/add")
def add(
    object_id: int,
    inspection_date: str = Form(...),
    inspector: str = Form(""),
    db: Session = Depends(get_db),
):
    insp = Inspection(
        object_id=object_id,
        date=date.fromisoformat(inspection_date),
        inspector=inspector,
    )
    SaveInspection(_repo(db)).execute(insp)
    return RedirectResponse(f"/objects/{object_id}/inspections/", status_code=303)


@router.post("/{inspection_id}/delete")
def delete(object_id: int, inspection_id: int, db: Session = Depends(get_db)):
    DeleteInspection(_repo(db)).execute(inspection_id)
    return RedirectResponse(f"/objects/{object_id}/inspections/", status_code=303)
