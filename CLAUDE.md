# CLAUDE.md

Этот файл содержит инструкции для Claude Code при работе с данным репозиторием.

## О проекте

**ohrana** — миграция legacy-системы управления охранным предприятием (Visual FoxPro 8) на Python/FastAPI.
Организация: **Ревдинский ОВО** (отдел вневедомственной охраны).
Назначение: учёт клиентов (юр. лиц) и охраняемых объектов, тарифы КТС/ПЦН, печать документов.

## Команды

```bash
uv run python run.py                                    # запустить приложение (открывается localhost:8080)
uv run python -m src.infrastructure.migration.migrate_dbf  # миграция DBF → SQLite (одноразово)
uv add <пакет>                                          # добавить зависимость (только uv, не pip)
```

## Архитектура

```
src/
├── domain/             # сущности и интерфейсы репозиториев (без зависимостей)
│   ├── entities/       # LegalEntity, GuardedObject, ObjectService, GuardSchedule, Inspection
│   └── repositories/   # ILegalEntityRepository, IObjectRepository, IInspectionRepository
├── application/
│   └── use_cases/      # GetAllLegalEntities, SaveObject, SaveObjectService и др.
├── infrastructure/
│   ├── database/       # SQLAlchemy модели (models.py) + сессия (session.py) → ohrana.db
│   ├── repositories/   # SQL-реализации интерфейсов
│   └── migration/      # migrate_dbf.py — одноразовый импорт из DBF
└── presentation/
    ├── app.py          # FastAPI приложение
    ├── routers/        # legal_entities, objects, inspections, documents
    ├── templates/      # Jinja2 + Bootstrap 5
    └── static/
```

**Правило зависимостей**: `presentation` → `application` → `domain` ← `infrastructure`

## База данных

SQLite, файл `ohrana.db` в корне проекта. Таблицы:

| Таблица | Содержимое |
|---------|-----------|
| `legal_entities` | Юр. лица: название, тип/номер договора, код |
| `objects` | Объекты охраны: название, адрес, телефон, подписант, дата принятия |
| `object_services` | Виды охраны (КТС/ПЦН) с тарифом, периодом, датами |
| `guard_schedules` | Время охраны: часы по рабочим/предпраздничным/выходным дням |
| `inspections` | Обследования объектов |

## Исходные данные (DBF, только для чтения)

- `DATA/` — основная база VFP (cp1251)
- `DATA_/` — зеркало
- `basa.dbf` → `legal_entities` + `objects` + `object_services`
- `time_kts.dbf`, `time_pul.dbf` → `guard_schedules`
- `obsled.dbf` → `inspections`

## Ссылки

- `ROADMAP.md` — план задач с текущим статусом
- `docs/info_for_migration.md` — исходное ТЗ
- `image/` — скриншоты оригинального VFP-интерфейса
