from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class LegalEntityModel(Base):
    __tablename__ = "legal_entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(20), default="Контракт")
    contract_number: Mapped[int] = mapped_column(Integer, default=0)
    code: Mapped[int | None] = mapped_column(Integer, nullable=True)

    objects: Mapped[list["GuardedObjectModel"]] = relationship(
        back_populates="legal_entity", cascade="all, delete-orphan"
    )


class GuardedObjectModel(Base):
    __tablename__ = "objects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    legal_entity_id: Mapped[int] = mapped_column(ForeignKey("legal_entities.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    town: Mapped[str] = mapped_column(String(50), default="")
    street: Mapped[str] = mapped_column(String(100), default="")
    phone: Mapped[str] = mapped_column(String(30), default="")
    signatory: Mapped[str] = mapped_column(String(100), default="")
    accepted_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    legal_entity: Mapped["LegalEntityModel"] = relationship(back_populates="objects")
    services: Mapped[list["ObjectServiceModel"]] = relationship(
        back_populates="obj", cascade="all, delete-orphan"
    )
    inspections: Mapped[list["InspectionModel"]] = relationship(
        back_populates="obj", cascade="all, delete-orphan"
    )


class ObjectServiceModel(Base):
    __tablename__ = "object_services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    object_id: Mapped[int] = mapped_column(ForeignKey("objects.id"), nullable=False)
    service_type: Mapped[str] = mapped_column(String(10), nullable=False)
    date_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    tariff: Mapped[float] = mapped_column(Float, default=0.0)
    period: Mapped[int] = mapped_column(Integer, default=12)

    obj: Mapped["GuardedObjectModel"] = relationship(back_populates="services")
    schedule: Mapped["GuardScheduleModel | None"] = relationship(
        back_populates="service", cascade="all, delete-orphan", uselist=False
    )


class GuardScheduleModel(Base):
    __tablename__ = "guard_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service_id: Mapped[int] = mapped_column(
        ForeignKey("object_services.id"), nullable=False, unique=True
    )

    work_start: Mapped[str] = mapped_column(String(5), default="08:00")
    work_end: Mapped[str] = mapped_column(String(5), default="18:00")
    days_off: Mapped[str] = mapped_column(String(30), default="суб.,вск.,праз")

    workday_from: Mapped[str] = mapped_column(String(5), default="18:00")
    workday_to: Mapped[str] = mapped_column(String(5), default="08:00")
    workday_count: Mapped[int] = mapped_column(Integer, default=0)

    preholiday_from: Mapped[str] = mapped_column(String(5), default="18:00")
    preholiday_to: Mapped[str] = mapped_column(String(5), default="08:00")
    preholiday_count: Mapped[int] = mapped_column(Integer, default=0)

    holiday_from: Mapped[str] = mapped_column(String(5), default="00:00")
    holiday_to: Mapped[str] = mapped_column(String(5), default="24:00")
    holiday_count: Mapped[int] = mapped_column(Integer, default=0)

    service: Mapped["ObjectServiceModel"] = relationship(back_populates="schedule")


class OrgSettingsModel(Base):
    """Реквизиты организации (из nastr.dbf)."""

    __tablename__ = "org_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chief_name: Mapped[str] = mapped_column(String(100), default="")
    chief_title: Mapped[str] = mapped_column(String(100), default="Начальник")
    org_name: Mapped[str] = mapped_column(String(500), default="")


class InspectionModel(Base):
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    object_id: Mapped[int] = mapped_column(ForeignKey("objects.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    inspector: Mapped[str] = mapped_column(String(100), default="")

    obj: Mapped["GuardedObjectModel"] = relationship(back_populates="inspections")
