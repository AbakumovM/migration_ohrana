"""Use cases для работы с юридическими лицами."""

from src.domain.entities.legal_entity import LegalEntity
from src.domain.repositories.legal_entity_repository import ILegalEntityRepository


class GetAllLegalEntities:
    """Возвращает список всех юридических лиц."""

    def __init__(self, repo: ILegalEntityRepository) -> None:
        self._repo = repo

    def execute(self) -> list[LegalEntity]:
        """Выполняет запрос всех юридических лиц, отсортированных по названию."""
        return self._repo.get_all()


class SearchLegalEntities:
    """Поиск юридических лиц по названию."""

    def __init__(self, repo: ILegalEntityRepository) -> None:
        self._repo = repo

    def execute(self, query: str) -> list[LegalEntity]:
        """Возвращает юридические лица, название которых содержит query (без учёта регистра)."""
        return self._repo.search(query)


class GetLegalEntity:
    """Возвращает юридическое лицо по идентификатору."""

    def __init__(self, repo: ILegalEntityRepository) -> None:
        self._repo = repo

    def execute(self, entity_id: int) -> LegalEntity | None:
        """Возвращает юридическое лицо или None, если не найдено."""
        return self._repo.get_by_id(entity_id)


class SaveLegalEntity:
    """Создаёт новое или обновляет существующее юридическое лицо."""

    def __init__(self, repo: ILegalEntityRepository) -> None:
        self._repo = repo

    def execute(self, entity: LegalEntity) -> LegalEntity:
        """Валидирует и сохраняет юридическое лицо.

        Raises:
            ValueError: Если название пустое.
        """
        if not entity.name.strip():
            raise ValueError("Название юр. лица не может быть пустым")
        return self._repo.save(entity)


class DeleteLegalEntity:
    """Удаляет юридическое лицо и все его объекты (каскад)."""

    def __init__(self, repo: ILegalEntityRepository) -> None:
        self._repo = repo

    def execute(self, entity_id: int) -> None:
        """Удаляет юридическое лицо по идентификатору."""
        self._repo.delete(entity_id)
