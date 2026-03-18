# Охрана — система управления объектами

Веб-приложение для учёта клиентов и охраняемых объектов Ревдинского ОВО.
Миграция с Visual FoxPro 8 на Python/FastAPI.

---

## Возможности

- **Юридические лица** — список с поиском по названию и номеру договора, создание, редактирование, удаление
- **Объекты охраны** — карточка объекта, виды охраны (КТС/ПЦН), тарифы, расписание, архив
- **Документы PDF** — перечень, расчёт, протокол согласования цены
- **Настройки** — реквизиты организации

---

## Запуск

### macOS

```bash
# Установить зависимости для WeasyPrint (генерация PDF)
brew install pango

# Установить зависимости проекта
uv sync

# Запустить
uv run python run.py
```

### Linux (Ubuntu / Debian)

```bash
sudo apt install -y libpango-1.0-0 libpangocairo-1.0-0 libcairo2 \
    libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

uv sync
uv run python run.py
```

### Windows

Пользователям Windows не нужно ничего устанавливать — скачать готовую сборку из раздела [Actions](../../actions) (артефакт `ohrana-windows`), распаковать и запустить `ohrana.exe`.

Браузер откроется автоматически. База данных хранится в папке рядом с `.exe`.

---

## Сборка Windows EXE

Сборка запускается автоматически через GitHub Actions на Windows-сервере.

**Разово (по тегу):**
```bash
git tag v1.0
git push --tags
```

**Вручную:** Actions → Build Windows EXE → Run workflow.

Скачать результат: вкладка Actions → нужный запуск → Artifacts → `ohrana-windows`.

---

## Команды разработки

```bash
uv run python run.py                                        # запуск (localhost:8080)
uv run python -m src.infrastructure.migration.migrate_dbf  # импорт DBF → SQLite (одноразово)
uv add <пакет>                                              # добавить зависимость
```

---

## Стек

Python 3.13 · FastAPI · SQLite · SQLAlchemy · Jinja2 · Bootstrap 5 · WeasyPrint · uv
