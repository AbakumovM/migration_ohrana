from src.domain.entities.guarded_object import GuardedObject
from src.domain.entities.object_service import ObjectService
from src.domain.repositories.object_repository import IObjectRepository


class GetObjectsByLegalEntity:
    def __init__(self, repo: IObjectRepository) -> None:
        self._repo = repo

    def execute(self, legal_entity_id: int) -> list[GuardedObject]:
        return self._repo.get_by_legal_entity(legal_entity_id)


class GetObject:
    def __init__(self, repo: IObjectRepository) -> None:
        self._repo = repo

    def execute(self, object_id: int) -> GuardedObject | None:
        return self._repo.get_by_id(object_id)


class SaveObject:
    def __init__(self, repo: IObjectRepository) -> None:
        self._repo = repo

    def execute(self, obj: GuardedObject) -> GuardedObject:
        if not obj.name.strip():
            raise ValueError("Название объекта не может быть пустым")
        return self._repo.save(obj)


class DeleteObject:
    def __init__(self, repo: IObjectRepository) -> None:
        self._repo = repo

    def execute(self, object_id: int) -> None:
        self._repo.delete(object_id)


class ArchiveObject:
    def __init__(self, repo: IObjectRepository) -> None:
        self._repo = repo

    def execute(self, object_id: int) -> None:
        self._repo.archive(object_id)


class GetObjectServices:
    def __init__(self, repo: IObjectRepository) -> None:
        self._repo = repo

    def execute(self, object_id: int) -> list[ObjectService]:
        return self._repo.get_services(object_id)


class SaveObjectService:
    def __init__(self, repo: IObjectRepository) -> None:
        self._repo = repo

    def execute(self, service: ObjectService) -> ObjectService:
        return self._repo.save_service(service)


class DeleteObjectService:
    def __init__(self, repo: IObjectRepository) -> None:
        self._repo = repo

    def execute(self, service_id: int) -> None:
        self._repo.delete_service(service_id)
