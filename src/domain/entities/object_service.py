from dataclasses import dataclass
from datetime import date
from enum import Enum


class ServiceType(str, Enum):
    KTS = "КТС"
    PUL = "ПЦН"


def _parse_hours(t: str) -> float:
    try:
        h, m = t.split(":")
        return int(h) + int(m) / 60
    except Exception:
        return 0.0


def _duration(start: str, end: str) -> float:
    s, e = _parse_hours(start), _parse_hours(end)
    return (e - s) if e >= s else (24 - s + e)


@dataclass
class GuardSchedule:
    """Время охраны (постановка на учёт) по виду охраны."""

    work_start: str = "08:00"
    work_end: str = "18:00"
    days_off: str = "суб.,вск.,праз"

    workday_from: str = "18:00"
    workday_to: str = "08:00"
    workday_count: int = 0

    preholiday_from: str = "18:00"
    preholiday_to: str = "08:00"
    preholiday_count: int = 0

    holiday_from: str = "00:00"
    holiday_to: str = "24:00"
    holiday_count: int = 0

    id: int | None = None

    @property
    def workday_hours(self) -> float:
        return _duration(self.workday_from, self.workday_to)

    @property
    def preholiday_hours(self) -> float:
        return _duration(self.preholiday_from, self.preholiday_to)

    @property
    def holiday_hours(self) -> float:
        return _duration(self.holiday_from, self.holiday_to)

    @property
    def total_hours(self) -> float:
        """Суммарное количество часов охраны за период."""
        return (
            self.workday_hours * self.workday_count
            + self.preholiday_hours * self.preholiday_count
            + self.holiday_hours * self.holiday_count
        )


@dataclass
class ObjectService:
    """Вид охраны (КТС или ПЦН) на конкретном объекте."""

    object_id: int
    service_type: ServiceType
    date_from: date | None = None
    date_to: date | None = None
    tariff: float = 0.0
    period: int = 12
    schedule: GuardSchedule | None = None
    id: int | None = None

    @property
    def monthly_sum(self) -> float:
        """Сумма за охрану в месяц: (total_hours / period) × tariff."""
        if self.schedule is None or self.period == 0:
            return 0.0
        return round((self.schedule.total_hours / self.period) * self.tariff, 2)
