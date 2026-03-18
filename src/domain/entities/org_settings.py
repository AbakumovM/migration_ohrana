from dataclasses import dataclass


@dataclass
class OrgSettings:
    """Реквизиты организации (начальник, должность, наименование ОВО)."""

    chief_name: str = ""
    chief_title: str = "Начальник"
    org_name: str = ""
    id: int | None = None
