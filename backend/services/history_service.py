import json
import os

from backend.config import settings
from backend.models.schemas import DialogueHistoryEntry


class HistoryService:
    """Управляет историей диалогов: хранение, добавление, чтение, очистка."""

    def __init__(self, history_file: str, max_messages: int):
        self.history_file = history_file
        self.max_messages = max_messages

    def _load(self) -> list:
        if not os.path.exists(self.history_file):
            return []
        with open(self.history_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, entries: list) -> None:
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2, default=str)

    def add_entry(self, operation_type: str, input_summary: str, result: dict) -> None:
        entry = DialogueHistoryEntry(
            operation_type=operation_type,
            input_summary=input_summary,
            result=result,
        )
        entries = self._load()
        entries.append(json.loads(entry.model_dump_json()))
        entries = entries[-self.max_messages :]
        self._save(entries)

    def get_all(self) -> list:
        return self._load()

    def clear(self) -> None:
        self._save([])


history_service = HistoryService(settings.HISTORY_FILE, settings.MAX_HISTORY_MESSAGES)
