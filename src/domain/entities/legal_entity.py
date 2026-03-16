from dataclasses import dataclass, field
from enum import Enum


class ContractType(str, Enum):
    CONTRACT = "Контракт"
    AGREEMENT = "Договор"


@dataclass
class LegalEntity:
    """Юридическое лицо (собственник объектов охраны)."""

    name: str
    contract_type: ContractType = ContractType.CONTRACT
    contract_number: int = 0
    code: int | None = None
    id: int | None = None
