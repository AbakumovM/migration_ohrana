from sqlalchemy.orm import Session

from src.domain.entities.legal_entity import ContractType, LegalEntity
from src.domain.repositories.legal_entity_repository import ILegalEntityRepository
from src.infrastructure.database.models import LegalEntityModel


def _to_entity(m: LegalEntityModel) -> LegalEntity:
    return LegalEntity(
        id=m.id,
        name=m.name,
        contract_type=ContractType(m.contract_type),
        contract_number=m.contract_number,
        code=m.code,
    )


def _to_model(e: LegalEntity, existing: LegalEntityModel | None = None) -> LegalEntityModel:
    m = existing or LegalEntityModel()
    m.name = e.name
    m.contract_type = e.contract_type.value
    m.contract_number = e.contract_number
    m.code = e.code
    return m


class SQLLegalEntityRepository(ILegalEntityRepository):

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_all(self) -> list[LegalEntity]:
        rows = self._db.query(LegalEntityModel).order_by(LegalEntityModel.name).all()
        return [_to_entity(r) for r in rows]

    def get_by_id(self, entity_id: int) -> LegalEntity | None:
        row = self._db.get(LegalEntityModel, entity_id)
        return _to_entity(row) if row else None

    def save(self, entity: LegalEntity) -> LegalEntity:
        if entity.id:
            existing = self._db.get(LegalEntityModel, entity.id)
            m = _to_model(entity, existing)
        else:
            m = _to_model(entity)
            self._db.add(m)
        self._db.commit()
        self._db.refresh(m)
        return _to_entity(m)

    def delete(self, entity_id: int) -> None:
        row = self._db.get(LegalEntityModel, entity_id)
        if row:
            self._db.delete(row)
            self._db.commit()
