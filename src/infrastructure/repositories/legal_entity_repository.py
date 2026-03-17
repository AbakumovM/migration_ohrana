"""SQL-реализация репозитория юридических лиц."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.domain.entities.legal_entity import ContractType, LegalEntity
from src.domain.repositories.legal_entity_repository import ILegalEntityRepository
from src.infrastructure.database.models import LegalEntityModel


def _to_entity(m: LegalEntityModel) -> LegalEntity:
    """Преобразует ORM-модель в доменную сущность LegalEntity."""
    return LegalEntity(
        id=m.id,
        name=m.name,
        contract_type=ContractType(m.contract_type),
        contract_number=m.contract_number,
        code=m.code,
    )


def _to_model(e: LegalEntity, existing: LegalEntityModel | None = None) -> LegalEntityModel:
    """Заполняет поля ORM-модели из доменной сущности. Использует existing если передан."""
    m = existing or LegalEntityModel()
    m.name = e.name
    m.contract_type = e.contract_type.value
    m.contract_number = e.contract_number
    m.code = e.code
    return m


class SQLLegalEntityRepository(ILegalEntityRepository):
    """Реализация ILegalEntityRepository через SQLAlchemy и SQLite."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_all(self) -> list[LegalEntity]:
        """Возвращает все юридические лица, отсортированные по названию."""
        rows = self._db.query(LegalEntityModel).order_by(LegalEntityModel.name).all()
        return [_to_entity(r) for r in rows]

    def get_next_contract_number(self) -> int:
        """Возвращает следующий свободный номер договора (MAX + 1)."""
        max_num = self._db.query(func.max(LegalEntityModel.contract_number)).scalar()
        return (max_num or 0) + 1

    def search(self, query: str) -> list[LegalEntity]:
        """Возвращает юридические лица, название которых содержит query (без учёта регистра)."""
        rows = (
            self._db.query(LegalEntityModel)
            .filter(LegalEntityModel.name.ilike(f"%{query}%"))
            .order_by(LegalEntityModel.name)
            .all()
        )
        return [_to_entity(r) for r in rows]

    def get_by_id(self, entity_id: int) -> LegalEntity | None:
        """Возвращает юридическое лицо по идентификатору или None, если не найдено."""
        row = self._db.get(LegalEntityModel, entity_id)
        return _to_entity(row) if row else None

    def save(self, entity: LegalEntity) -> LegalEntity:
        """Сохраняет юридическое лицо. Создаёт новое, если id равен None; обновляет существующее иначе."""
        if entity.id:
            m = self._db.get(LegalEntityModel, entity.id)
            if m is None:
                raise ValueError(f"LegalEntity id={entity.id} не найдена в БД")
            _to_model(entity, m)
        else:
            m = _to_model(entity)
            self._db.add(m)
        self._db.commit()
        self._db.refresh(m)
        return _to_entity(m)

    def delete(self, entity_id: int) -> None:
        """Удаляет юридическое лицо и все связанные объекты (каскад)."""
        row = self._db.get(LegalEntityModel, entity_id)
        if row:
            self._db.delete(row)
            self._db.commit()
