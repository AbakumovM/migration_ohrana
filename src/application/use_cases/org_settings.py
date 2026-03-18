"""Use cases для работы с реквизитами организации."""

from src.domain.entities.org_settings import OrgSettings
from src.domain.repositories.org_settings_repository import IOrgSettingsRepository


class GetOrgSettings:
    """Возвращает реквизиты организации."""

    def __init__(self, repo: IOrgSettingsRepository) -> None:
        self._repo = repo

    def execute(self) -> OrgSettings | None:
        """Возвращает реквизиты или None, если ещё не заданы."""
        return self._repo.get()


class SaveOrgSettings:
    """Сохраняет реквизиты организации."""

    def __init__(self, repo: IOrgSettingsRepository) -> None:
        self._repo = repo

    def execute(self, settings: OrgSettings) -> OrgSettings:
        """Сохраняет и возвращает обновлённые реквизиты."""
        return self._repo.save(settings)
