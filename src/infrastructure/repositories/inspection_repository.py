from sqlalchemy.orm import Session

from src.domain.entities.inspection import Inspection
from src.domain.repositories.inspection_repository import IInspectionRepository
from src.infrastructure.database.models import InspectionModel


def _to_entity(m: InspectionModel) -> Inspection:
    return Inspection(id=m.id, object_id=m.object_id, date=m.date, inspector=m.inspector)


class SQLInspectionRepository(IInspectionRepository):

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_object(self, object_id: int) -> list[Inspection]:
        rows = (
            self._db.query(InspectionModel)
            .filter_by(object_id=object_id)
            .order_by(InspectionModel.date.desc())
            .all()
        )
        return [_to_entity(r) for r in rows]

    def save(self, inspection: Inspection) -> Inspection:
        if inspection.id:
            m = self._db.get(InspectionModel, inspection.id)
        else:
            m = InspectionModel()
            self._db.add(m)
        m.object_id = inspection.object_id
        m.date = inspection.date
        m.inspector = inspection.inspector
        self._db.commit()
        self._db.refresh(m)
        return _to_entity(m)

    def delete(self, inspection_id: int) -> None:
        row = self._db.get(InspectionModel, inspection_id)
        if row:
            self._db.delete(row)
            self._db.commit()
