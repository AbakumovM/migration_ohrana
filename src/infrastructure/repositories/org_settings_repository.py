"""SQL-реализация репозитория реквизитов организации."""

from sqlalchemy.orm import Session

from src.domain.entities.org_settings import OrgSettings
from src.domain.repositories.org_settings_repository import IOrgSettingsRepository
from src.infrastructure.database.models import OrgSettingsModel


def _to_entity(m: OrgSettingsModel) -> OrgSettings:
    return OrgSettings(id=m.id, chief_name=m.chief_name, chief_title=m.chief_title, org_name=m.org_name)


class SQLOrgSettingsRepository(IOrgSettingsRepository):
    """Реализация IOrgSettingsRepository через SQLAlchemy и SQLite."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self) -> OrgSettings | None:
        """Возвращает реквизиты организации или None, если ещё не заданы."""
        row = self._db.query(OrgSettingsModel).first()
        return _to_entity(row) if row else None

    def save(self, settings: OrgSettings) -> OrgSettings:
        """Сохраняет реквизиты организации. Создаёт запись, если её нет."""
        row = self._db.query(OrgSettingsModel).first()
        if row is None:
            row = OrgSettingsModel()
            self._db.add(row)
        row.chief_name = settings.chief_name
        row.chief_title = settings.chief_title
        row.org_name = settings.org_name
        self._db.commit()
        self._db.refresh(row)
        return _to_entity(row)
