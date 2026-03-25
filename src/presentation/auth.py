"""Логика авторизации: проверка credentials, хэш пароля."""

import hashlib
import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY: str = os.environ.get("SECRET_KEY", "insecure-default-key-change-me")
AUTH_USERNAME: str = os.environ.get("AUTH_USERNAME", "admin")
AUTH_PASSWORD_HASH: str = os.environ.get("AUTH_PASSWORD_HASH", "")


def hash_password(password: str) -> str:
    """Возвращает SHA-256 хэш пароля."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_credentials(username: str, password: str) -> bool:
    """Проверяет логин и пароль по переменным окружения."""
    return username == AUTH_USERNAME and hash_password(password) == AUTH_PASSWORD_HASH
