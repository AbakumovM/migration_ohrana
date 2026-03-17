from abc import ABC, abstractmethod

from src.domain.entities.guarded_object import GuardedObject
from src.domain.entities.object_service import ObjectService


class IObjectRepository(ABC):
    """Интерфейс репозитория охраняемых объектов и их видов охраны."""

    @abstractmethod
    def count_active_by_legal_entities(self) -> dict[int, int]:
        """Возвращает словарь {legal_entity_id: количество активных объектов} для всех юр. лиц."""
        ...

    @abstractmethod
    def get_by_legal_entity(self, legal_entity_id: int) -> list[GuardedObject]:
        """Возвращает все активные (не архивные) объекты указанного юридического лица."""
        ...

    @abstractmethod
    def get_archived(self, legal_entity_id: int) -> list[GuardedObject]:
        """Возвращает архивные объекты указанного юридического лица."""
        ...

    @abstractmethod
    def get_by_id(self, object_id: int) -> GuardedObject | None:
        """Возвращает объект по идентификатору или None, если не найден."""
        ...

    @abstractmethod
    def save(self, obj: GuardedObject) -> GuardedObject:
        """Сохраняет объект. Создаёт новый, если id равен None; обновляет существующий иначе."""
        ...

    @abstractmethod
    def delete(self, object_id: int) -> None:
        """Удаляет объект и все связанные записи (виды охраны, обследования)."""
        ...

    @abstractmethod
    def archive(self, object_id: int) -> None:
        """Переводит объект в архив (устанавливает is_archived = True)."""
        ...

    @abstractmethod
    def get_services(self, object_id: int) -> list[ObjectService]:
        """Возвращает все виды охраны (с расписанием) для указанного объекта."""
        ...

    @abstractmethod
    def save_service(self, service: ObjectService) -> ObjectService:
        """Сохраняет вид охраны вместе с расписанием. Создаёт или обновляет."""
        ...

    @abstractmethod
    def delete_service(self, service_id: int) -> None:
        """Удаляет вид охраны и связанное расписание."""
        ...
