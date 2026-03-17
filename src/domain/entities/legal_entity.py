from dataclasses import dataclass
from enum import Enum


class ContractType(str, Enum):
    """Тип договора с юридическим лицом."""

    CONTRACT = "Контракт"
    AGREEMENT = "Договор"

    @property
    def dative(self) -> str:
        """Форма дательного падежа для предложного оборота 'к Договору'."""
        return self.value + "у"


@dataclass
class LegalEntity:
    """Юридическое лицо (собственник объектов охраны)."""

    name: str
    contract_type: ContractType = ContractType.AGREEMENT
    contract_number: int = 0
    code: int | None = None
    id: int | None = None
