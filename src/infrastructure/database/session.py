"""Настройка подключения к базе данных SQLite и фабрика сессий."""

import sys
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# При запуске из .exe (PyInstaller frozen) храним БД рядом с исполняемым файлом,
# при обычном запуске — в корне проекта.
if getattr(sys, "frozen", False):
    DB_PATH = Path(sys.executable).parent / "ohrana.db"
else:
    DB_PATH = Path(__file__).parents[3] / "ohrana.db"
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """Генератор сессии БД для FastAPI Depends. Закрывает сессию после запроса."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
