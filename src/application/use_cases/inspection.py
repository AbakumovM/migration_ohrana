from src.domain.entities.inspection import Inspection
from src.domain.repositories.inspection_repository import IInspectionRepository


class GetInspectionsByObject:
    def __init__(self, repo: IInspectionRepository) -> None:
        self._repo = repo

    def execute(self, object_id: int) -> list[Inspection]:
        return self._repo.get_by_object(object_id)


class SaveInspection:
    def __init__(self, repo: IInspectionRepository) -> None:
        self._repo = repo

    def execute(self, inspection: Inspection) -> Inspection:
        return self._repo.save(inspection)


class DeleteInspection:
    def __init__(self, repo: IInspectionRepository) -> None:
        self._repo = repo

    def execute(self, inspection_id: int) -> None:
        self._repo.delete(inspection_id)
