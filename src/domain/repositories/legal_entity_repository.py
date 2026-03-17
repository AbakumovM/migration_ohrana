from abc import ABC, abstractmethod

from src.domain.entities.legal_entity import LegalEntity


class ILegalEntityRepository(ABC):
    """Интерфейс репозитория юридических лиц."""

    @abstractmethod
    def get_all(self) -> list[LegalEntity]:
        """Возвращает все юридические лица."""
        ...

    @abstractmethod
    def get_next_contract_number(self) -> int:
        """Возвращает следующий свободный номер договора (MAX + 1)."""
        ...

    @abstractmethod
    def search(self, query: str) -> list[LegalEntity]:
        """Возвращает юридические лица, название которых содержит query (без учёта регистра)."""
        ...

    @abstractmethod
    def get_by_id(self, entity_id: int) -> LegalEntity | None:
        """Возвращает юридическое лицо по идентификатору или None, если не найдено."""
        ...

    @abstractmethod
    def save(self, entity: LegalEntity) -> LegalEntity:
        """Сохраняет юридическое лицо. Создаёт новое, если id равен None; обновляет существующее иначе."""
        ...

    @abstractmethod
    def delete(self, entity_id: int) -> None:
        """Удаляет юридическое лицо и все связанные объекты (каскад)."""
        ...
