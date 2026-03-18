"""Настройка подключения к базе данных SQLite и фабрика сессий."""

import sys
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# При запуске из .exe (PyInstaller) — БД в ~/ohrana/, не зависит от папки приложения.
# При обычном запуске — в корне проекта.
if getattr(sys, "frozen", False):
    DB_PATH = Path.home() / "ohrana" / "ohrana.db"
    DB_PATH.parent.mkdir(exist_ok=True)
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
