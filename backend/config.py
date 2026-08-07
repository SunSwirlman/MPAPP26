import os
import sys

from dotenv import load_dotenv

# В собранном .exe (PyInstaller) __file__ указывает на временную распаковку —
# .env и history.json должны жить рядом с самим исполняемым файлом, а не там.
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(BASE_DIR, ".env"))


class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    TEXT_MODEL = "gpt-4o-mini"
    VISION_MODEL = "gpt-4o-mini"

    HOST = "127.0.0.1"
    PORT = 8000

    HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
    MAX_HISTORY_MESSAGES = 10

    NICHE = "Персональные цифровые аватары"
    COMPETITOR_URLS = {
        "Synthesia": "https://www.synthesia.io/",
        "HeyGen": "https://www.heygen.com/",
        "D-ID": "https://www.d-id.com/",
    }


settings = Settings()
