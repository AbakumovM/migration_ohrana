"""Точка входа. Запуск: uv run python run.py"""
import os
import sys
import webbrowser
import threading
import time

# На macOS Homebrew-библиотеки (Pango/GLib) нужны для WeasyPrint
if sys.platform == "darwin":
    brew_lib = "/opt/homebrew/lib"
    current = os.environ.get("DYLD_LIBRARY_PATH", "")
    if brew_lib not in current:
        os.environ["DYLD_LIBRARY_PATH"] = f"{brew_lib}:{current}".strip(":")

import uvicorn


def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:8080")


if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(
        "src.presentation.app:app",
        host="127.0.0.1",
        port=8080,
        reload=False,
    )
