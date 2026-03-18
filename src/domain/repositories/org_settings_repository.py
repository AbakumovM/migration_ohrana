from abc import ABC, abstractmethod

from src.domain.entities.org_settings import OrgSettings


class IOrgSettingsRepository(ABC):
    """Интерфейс репозитория реквизитов организации."""

    @abstractmethod
    def get(self) -> OrgSettings | None:
        """Возвращает реквизиты организации или None, если ещё не заданы."""
        ...

    @abstractmethod
    def save(self, settings: OrgSettings) -> OrgSettings:
        """Сохраняет реквизиты организации. Создаёт запись, если её нет."""
        ...
