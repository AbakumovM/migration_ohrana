"""Use cases для работы с охраняемыми объектами и видами охраны."""

from src.domain.entities.guarded_object import GuardedObject
from src.domain.entities.object_service import ObjectService
from src.domain.repositories.object_repository import IObjectRepository


class GetObjectsByLegalEntity:
    """Возвращает активные объекты охраны для указанного юридического лица."""

    def __init__(self, repo: IObjectRepository) -> None:
        self._repo = repo

    def execute(self, legal_entity_id: int) -> list[GuardedObject]:
        """Выполняет запрос активных объектов, отсортированных по названию."""
        return self._repo.get_by_legal_entity(legal_entity_id)


class GetObject:
    """Возвращает охраняемый объект по идентификатору."""

    def __init__(self, repo: IObjectRepository) -> None:
        self._repo = repo

    def execute(self, object_id: int) -> GuardedObject | None:
        """Возвращает объект или None, если не найден."""
        return self._repo.get_by_id(object_id)


class SaveObject:
    """Создаёт новый или обновляет существующий охраняемый объект."""

    def __init__(self, repo: IObjectRepository) -> None:
        self._repo = repo

    def execute(self, obj: GuardedObject) -> GuardedObject:
        """Валидирует и сохраняет объект.

        Raises:
            ValueError: Если название объекта пустое.
        """
        if not obj.name.strip():
            raise ValueError("Название объекта не может быть пустым")
        return self._repo.save(obj)


class DeleteObject:
    """Удаляет охраняемый объект и все связанные данные."""

    def __init__(self, repo: IObjectRepository) -> None:
        self._repo = repo

    def execute(self, object_id: int) -> None:
        """Удаляет объект по идентификатору."""
        self._repo.delete(object_id)


class ArchiveObject:
    """Переводит охраняемый объект в архив."""

    def __init__(self, repo: IObjectRepository) -> None:
        self._repo = repo

    def execute(self, object_id: int) -> None:
        """Устанавливает is_archived = True для объекта."""
        self._repo.archive(object_id)


class GetObjectServices:
    """Возвращает виды охраны для указанного объекта."""

    def __init__(self, repo: IObjectRepository) -> None:
        self._repo = repo

    def execute(self, object_id: int) -> list[ObjectService]:
        """Возвращает список видов охраны с расписанием."""
        return self._repo.get_services(object_id)


class SaveObjectService:
    """Создаёт новый или обновляет существующий вид охраны с расписанием."""

    def __init__(self, repo: IObjectRepository) -> None:
        self._repo = repo

    def execute(self, service: ObjectService) -> ObjectService:
        """Сохраняет вид охраны вместе с расписанием."""
        return self._repo.save_service(service)


class DeleteObjectService:
    """Удаляет вид охраны и связанное расписание."""

    def __init__(self, repo: IObjectRepository) -> None:
        self._repo = repo

    def execute(self, service_id: int) -> None:
        """Удаляет вид охраны по идентификатору."""
        self._repo.delete_service(service_id)
