from abc import ABC, abstractmethod

from src.domain.entities.legal_entity import LegalEntity


class ILegalEntityRepository(ABC):

    @abstractmethod
    def get_all(self) -> list[LegalEntity]: ...

    @abstractmethod
    def get_by_id(self, entity_id: int) -> LegalEntity | None: ...

    @abstractmethod
    def save(self, entity: LegalEntity) -> LegalEntity: ...

    @abstractmethod
    def delete(self, entity_id: int) -> None: ...
