from dataclasses import dataclass, field
from datetime import date


@dataclass
class GuardedObject:
    """Охраняемый объект, принадлежащий юридическому лицу."""

    legal_entity_id: int
    name: str
    town: str = ""
    street: str = ""
    phone: str = ""
    signatory: str = ""
    accepted_date: date | None = None
    is_archived: bool = False
    id: int | None = None
