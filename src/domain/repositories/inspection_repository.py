from abc import ABC, abstractmethod

from src.domain.entities.inspection import Inspection


class IInspectionRepository(ABC):

    @abstractmethod
    def get_by_object(self, object_id: int) -> list[Inspection]: ...

    @abstractmethod
    def save(self, inspection: Inspection) -> Inspection: ...

    @abstractmethod
    def delete(self, inspection_id: int) -> None: ...
