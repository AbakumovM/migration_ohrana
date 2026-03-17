from dataclasses import dataclass
from enum import Enum


class ContractType(str, Enum):
    """Тип договора с юридическим лицом."""

    CONTRACT = "Контракт"
    AGREEMENT = "Договор"


@dataclass
class LegalEntity:
    """Юридическое лицо (собственник объектов охраны)."""

    name: str
    contract_type: ContractType = ContractType.AGREEMENT
    contract_number: int = 0
    code: int | None = None
    id: int | None = None
