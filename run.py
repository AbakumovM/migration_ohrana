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
from src.presentation.app import app


def _make_icon():
    """Создаёт простую иконку щита для системного трея."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (64, 64), color=(25, 55, 110))
    draw = ImageDraw.Draw(img)
    draw.polygon([(32, 6), (58, 20), (58, 42), (32, 58), (6, 42), (6, 20)], fill=(255, 255, 255))
    draw.polygon([(32, 14), (50, 26), (50, 40), (32, 52), (14, 40), (14, 26)], fill=(25, 55, 110))
    return img


def _open_browser():
    time.sleep(1.5)
    webbrowser.open("http://localhost:8080")


if __name__ == "__main__":
    config = uvicorn.Config(app, host="127.0.0.1", port=8080, log_config=None)
    server = uvicorn.Server(config)

    threading.Thread(target=server.run, daemon=True).start()
    threading.Thread(target=_open_browser, daemon=True).start()

    # Иконка в трее только на Windows
    if sys.platform == "win32":
        import pystray

        def _on_open(icon, item):
            webbrowser.open("http://localhost:8080")

        def _on_exit(icon, item):
            server.should_exit = True
            icon.stop()

        tray = pystray.Icon(
            "ohrana",
            _make_icon(),
            "Охрана",
            menu=pystray.Menu(
                pystray.MenuItem("Открыть в браузере", _on_open),
                pystray.MenuItem("Выход", _on_exit),
            ),
        )
        tray.run()
    else:
        # На macOS/Linux просто ждём завершения
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            server.should_exit = True
