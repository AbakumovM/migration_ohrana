# REVIEW — Детальная проверка по блокам

## Статус блоков

| # | Блок | Статус | Результат |
|---|------|--------|-----------|
| 1 | Domain layer (сущности + интерфейсы репозиториев) | ✅ Закрыт | Docstrings, удалены обследования, исправлен тариф, счётчик объектов |
| 2 | Инфраструктура (SQLAlchemy модели + SQL-репозитории) | ✅ Закрыт | Docstrings, исправлены 3 бага save(), поиск через SQL |
| 3 | Юридические лица (use cases + роутер + шаблоны) | ⏳ Ожидает | — |
| 4 | Объекты охраны (use cases + роутер + виды охраны + расписание) | ⏳ Ожидает | — |
| 5 | ~~Обследования~~ | 🚫 Удалено | Функциональность не нужна |
| 6 | Документы PDF (роутер + шаблоны) | ✅ Закрыт | Альбомная ориентация, двойные отступы, репозиторий вместо ORM |
| 7 | Миграция DBF → SQLite | ✅ Закрыт | Исправлен баг db.close(), перемещена _attach_schedule, type hints и docstrings |

---

## Блок 1 — Domain layer

**Файлы:**
- `src/domain/entities/legal_entity.py`
- `src/domain/entities/guarded_object.py`
- `src/domain/entities/object_service.py`
- `src/domain/entities/inspection.py`
- `src/domain/repositories/legal_entity_repository.py`
- `src/domain/repositories/object_repository.py`
- `src/domain/repositories/inspection_repository.py`

### Чеклист

#### Сущности (entities)

- [x] `ContractType` — docstring добавлен
- [x] `LegalEntity` — структура корректна; поля типизированы
- [x] `LegalEntity.contract_number: int` — подтверждено: только числа
- [x] `LegalEntity.code` — уточнено: внутренний числовой код из VFP
- [x] `legal_entity.py` — лишний импорт `field` удалён
- [x] `ServiceType` — docstring добавлен
- [x] `_parse_hours` — docstring добавлен
- [x] `_duration` — docstring добавлен
- [x] `GuardSchedule.workday_hours` — docstring добавлен
- [x] `GuardSchedule.preholiday_hours` — docstring добавлен
- [x] `GuardSchedule.holiday_hours` — docstring добавлен
- [x] `GuardSchedule` без `service_id` — норма: FK только в БД, доступ через `ObjectService.schedule`
- [x] `guarded_object.py` — лишний импорт `field` удалён

#### Репозитории (интерфейсы)

- [x] `ILegalEntityRepository` — docstring на классе и всех методах
- [x] `ILegalEntityRepository.search` — добавлен новый метод (поиск по названию)
- [x] `IObjectRepository` — docstring на классе и всех методах
- [x] `IObjectRepository.get_archived` — добавлен новый метод (архивные объекты)
- [x] `IInspectionRepository` — docstring на классе и всех методах

#### Архитектура

- [x] Нет импортов SQLAlchemy / infrastructure в domain
- [x] Бизнес-логика расчёта (`monthly_sum`, `total_hours`) — в entities, не в роутерах
- [x] `IObjectRepository` совмещает объект и сервисы — осознанное решение для небольшого приложения

---

## Блок 2 — Инфраструктура

*(заполняется после Блока 1)*

---

## Блок 3 — Юридические лица

*(заполняется после Блока 2)*

---

## Блок 4 — Объекты охраны

*(заполняется после Блока 3)*

---

## Блок 5 — Обследования

*(заполняется после Блока 4)*

---

## Блок 6 — Документы PDF

*(заполняется после Блока 5)*

---

## Блок 7 — Миграция DBF → SQLite

**Файл:** `src/infrastructure/migration/migrate_dbf.py`

### Чеклист

- [x] Баг с закрытой сессией исправлен — `db.close()` перенесён в конец `migrate()`
- [x] `_attach_schedule` перемещена перед `migrate()` (порядок объявления)
- [x] `_str` — добавлены type hints и docstring
- [x] `_parse_time` — добавлены type hints и docstring
- [x] `_attach_schedule` — добавлены type hints (`db: Session`) и docstring
- [x] `ruff check` — без ошибок
- [x] `mypy` — без ошибок (28 файлов)
