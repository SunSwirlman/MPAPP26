"""Сборка standalone-приложения CompetitionMonitor.exe через PyInstaller.

Запуск: python build.py
Результат: dist/CompetitionMonitor.exe
API-ключ НЕ встраивается в exe — .env нужно положить рядом с готовым файлом.
"""
import PyInstaller.__main__

PyInstaller.__main__.run(
    [
        "desktop/main.py",
        "--name=CompetitionMonitor",
        "--onefile",
        "--windowed",
        "--noconfirm",
    ]
)
