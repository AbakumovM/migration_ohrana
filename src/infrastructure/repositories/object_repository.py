"""SQL-реализация репозитория охраняемых объектов и видов охраны."""

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from src.domain.entities.guarded_object import GuardedObject
from src.domain.entities.object_service import GuardSchedule, ObjectService, ServiceType
from src.domain.repositories.object_repository import IObjectRepository
from src.infrastructure.database.models import (
    GuardScheduleModel,
    GuardedObjectModel,
    ObjectServiceModel,
)


def _to_object(m: GuardedObjectModel) -> GuardedObject:
    """Преобразует ORM-модель объекта в доменную сущность GuardedObject."""
    return GuardedObject(
        id=m.id,
        legal_entity_id=m.legal_entity_id,
        name=m.name,
        town=m.town,
        street=m.street,
        phone=m.phone,
        signatory=m.signatory,
        accepted_date=m.accepted_date,
        is_archived=m.is_archived,
    )


def _to_schedule(m: GuardScheduleModel) -> GuardSchedule:
    """Преобразует ORM-модель расписания в доменную сущность GuardSchedule."""
    return GuardSchedule(
        id=m.id,
        work_start=m.work_start,
        work_end=m.work_end,
        days_off=m.days_off,
        workday_from=m.workday_from,
        workday_to=m.workday_to,
        workday_count=m.workday_count,
        preholiday_from=m.preholiday_from,
        preholiday_to=m.preholiday_to,
        preholiday_count=m.preholiday_count,
        holiday_from=m.holiday_from,
        holiday_to=m.holiday_to,
        holiday_count=m.holiday_count,
    )


def _to_service(m: ObjectServiceModel) -> ObjectService:
    """Преобразует ORM-модель вида охраны в доменную сущность ObjectService."""
    return ObjectService(
        id=m.id,
        object_id=m.object_id,
        service_type=ServiceType(m.service_type),
        date_from=m.date_from,
        date_to=m.date_to,
        tariff=m.tariff,
        period=m.period,
        schedule=_to_schedule(m.schedule) if m.schedule else None,
    )


class SQLObjectRepository(IObjectRepository):
    """Реализация IObjectRepository через SQLAlchemy и SQLite."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def count_active_by_legal_entities(self) -> dict[int, int]:
        """Возвращает словарь {legal_entity_id: количество активных объектов} для всех юр. лиц."""
        rows = (
            self._db.query(GuardedObjectModel.legal_entity_id, func.count(GuardedObjectModel.id))
            .filter_by(is_archived=False)
            .group_by(GuardedObjectModel.legal_entity_id)
            .all()
        )
        return {le_id: count for le_id, count in rows}

    def get_by_legal_entity(self, legal_entity_id: int) -> list[GuardedObject]:
        """Возвращает все активные (не архивные) объекты указанного юридического лица."""
        rows = (
            self._db.query(GuardedObjectModel)
            .filter_by(legal_entity_id=legal_entity_id, is_archived=False)
            .order_by(GuardedObjectModel.name)
            .all()
        )
        return [_to_object(r) for r in rows]

    def get_archived(self, legal_entity_id: int) -> list[GuardedObject]:
        """Возвращает архивные объекты указанного юридического лица."""
        rows = (
            self._db.query(GuardedObjectModel)
            .filter_by(legal_entity_id=legal_entity_id, is_archived=True)
            .order_by(GuardedObjectModel.name)
            .all()
        )
        return [_to_object(r) for r in rows]

    def get_by_id(self, object_id: int) -> GuardedObject | None:
        """Возвращает объект по идентификатору или None, если не найден."""
        row = self._db.get(GuardedObjectModel, object_id)
        return _to_object(row) if row else None

    def save(self, obj: GuardedObject) -> GuardedObject:
        """Сохраняет объект. Создаёт новый, если id равен None; обновляет существующий иначе."""
        if obj.id:
            m = self._db.get(GuardedObjectModel, obj.id)
            if m is None:
                raise ValueError(f"GuardedObject id={obj.id} не найден в БД")
        else:
            m = GuardedObjectModel()
            self._db.add(m)
        m.legal_entity_id = obj.legal_entity_id
        m.name = obj.name
        m.town = obj.town
        m.street = obj.street
        m.phone = obj.phone
        m.signatory = obj.signatory
        m.accepted_date = obj.accepted_date
        m.is_archived = obj.is_archived
        self._db.commit()
        self._db.refresh(m)
        return _to_object(m)

    def delete(self, object_id: int) -> None:
        """Удаляет объект и все связанные записи (виды охраны)."""
        row = self._db.get(GuardedObjectModel, object_id)
        if row:
            self._db.delete(row)
            self._db.commit()

    def archive(self, object_id: int) -> None:
        """Переводит объект в архив (устанавливает is_archived = True)."""
        row = self._db.get(GuardedObjectModel, object_id)
        if row:
            row.is_archived = True
            self._db.commit()

    def get_services(self, object_id: int) -> list[ObjectService]:
        """Возвращает все виды охраны с расписанием для указанного объекта."""
        rows = (
            self._db.query(ObjectServiceModel)
            .options(joinedload(ObjectServiceModel.schedule))
            .filter_by(object_id=object_id)
            .all()
        )
        return [_to_service(r) for r in rows]

    def save_service(self, service: ObjectService) -> ObjectService:
        """Сохраняет вид охраны вместе с расписанием. Создаёт или обновляет."""
        if service.id:
            m = self._db.get(ObjectServiceModel, service.id)
            if m is None:
                raise ValueError(f"ObjectService id={service.id} не найден в БД")
        else:
            m = ObjectServiceModel()
            self._db.add(m)
        m.object_id = service.object_id
        m.service_type = service.service_type.value
        m.date_from = service.date_from
        m.date_to = service.date_to
        m.tariff = service.tariff
        m.period = service.period

        if service.schedule:
            if m.schedule is None:
                m.schedule = GuardScheduleModel()
            s = m.schedule
            s.work_start = service.schedule.work_start
            s.work_end = service.schedule.work_end
            s.days_off = service.schedule.days_off
            s.workday_from = service.schedule.workday_from
            s.workday_to = service.schedule.workday_to
            s.workday_count = service.schedule.workday_count
            s.preholiday_from = service.schedule.preholiday_from
            s.preholiday_to = service.schedule.preholiday_to
            s.preholiday_count = service.schedule.preholiday_count
            s.holiday_from = service.schedule.holiday_from
            s.holiday_to = service.schedule.holiday_to
            s.holiday_count = service.schedule.holiday_count

        self._db.commit()
        self._db.refresh(m)
        return _to_service(m)

    def delete_service(self, service_id: int) -> None:
        """Удаляет вид охраны и связанное расписание."""
        row = self._db.get(ObjectServiceModel, service_id)
        if row:
            self._db.delete(row)
            self._db.commit()
