from src.domain.entities.legal_entity import LegalEntity
from src.domain.repositories.legal_entity_repository import ILegalEntityRepository


class GetAllLegalEntities:
    def __init__(self, repo: ILegalEntityRepository) -> None:
        self._repo = repo

    def execute(self) -> list[LegalEntity]:
        return self._repo.get_all()


class GetLegalEntity:
    def __init__(self, repo: ILegalEntityRepository) -> None:
        self._repo = repo

    def execute(self, entity_id: int) -> LegalEntity | None:
        return self._repo.get_by_id(entity_id)


class SaveLegalEntity:
    def __init__(self, repo: ILegalEntityRepository) -> None:
        self._repo = repo

    def execute(self, entity: LegalEntity) -> LegalEntity:
        if not entity.name.strip():
            raise ValueError("Название юр. лица не может быть пустым")
        return self._repo.save(entity)


class DeleteLegalEntity:
    def __init__(self, repo: ILegalEntityRepository) -> None:
        self._repo = repo

    def execute(self, entity_id: int) -> None:
        self._repo.delete(entity_id)
