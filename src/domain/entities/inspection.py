from dataclasses import dataclass
from datetime import date


@dataclass
class Inspection:
    """Обследование охраняемого объекта."""

    object_id: int
    date: date
    inspector: str = ""
    id: int | None = None
