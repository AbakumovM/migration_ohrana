from abc import ABC, abstractmethod

from src.domain.entities.guarded_object import GuardedObject
from src.domain.entities.object_service import ObjectService


class IObjectRepository(ABC):

    @abstractmethod
    def get_by_legal_entity(self, legal_entity_id: int) -> list[GuardedObject]: ...

    @abstractmethod
    def get_by_id(self, object_id: int) -> GuardedObject | None: ...

    @abstractmethod
    def save(self, obj: GuardedObject) -> GuardedObject: ...

    @abstractmethod
    def delete(self, object_id: int) -> None: ...

    @abstractmethod
    def archive(self, object_id: int) -> None: ...

    @abstractmethod
    def get_services(self, object_id: int) -> list[ObjectService]: ...

    @abstractmethod
    def save_service(self, service: ObjectService) -> ObjectService: ...

    @abstractmethod
    def delete_service(self, service_id: int) -> None: ...
