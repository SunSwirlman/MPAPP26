# MPAPP26 — Competitor Analysis Assistant

Мультимодальный AI-ассистент для анализа конкурентов. Ниша кейса: **персональные цифровые
аватары** (AI-видео с говорящими аватарами) — проанализированы Synthesia, HeyGen и D-ID.

Три интерфейса поверх одной бизнес-логики:
- **Web UI** (FastAPI + vanilla JS) — форма с вкладками текст/изображение/парсинг/история
- **Desktop** (PyQt6, standalone `.exe` через PyInstaller)
- Telegram-бот — вне скопа текущей версии

## Возможности

- **Анализ текста** — сильные/слабые стороны, уникальные предложения, рекомендации (JSON)
- **Анализ изображений** — маркетинговые инсайты, `visual_style_score`, а также кастомные
  под нашу нишу поля `design_score` и `animation_potential` (потенциал "оживления" материала
  через AI-аватара)
- **Парсинг сайтов конкурентов** через Selenium (headless Chrome) + автоанализ извлечённого текста
- **История диалогов** — последние 10 операций, хранится в `history.json`

## Архитектура

```
backend/
  config.py            — настройки, ключи, модели, URL конкурентов
  main.py              — FastAPI-приложение и эндпоинты
  models/schemas.py     — Pydantic-модели запросов/ответов
  services/
    history_service.py  — синглтон истории диалогов
    openai_service.py   — вызовы OpenAI (gpt-4o-mini), системные промпты
    parsing_service.py  — Selenium-парсинг сайтов
frontend/                — Web UI (HTML/CSS/JS)
desktop/                  — PyQt6 приложение (использует backend/services напрямую)
data/                      — собранные тексты и изображения конкурентов
build.py                   — сборка desktop/main.py в CompetitionMonitor.exe
run.py                     — запуск веб-сервера (uvicorn run:app --reload)
```

## Запуск (Web)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# создать .env с OPENAI_API_KEY=...
uvicorn run:app --reload
# открыть http://127.0.0.1:8000
```

## Запуск (Desktop)

```bash
python desktop/main.py
```

## Сборка standalone .exe

```bash
python build.py
# результат: dist/CompetitionMonitor.exe
# рядом с exe нужно положить .env с OPENAI_API_KEY — ключ не встраивается в бинарник
```

## API-эндпоинты

| Метод | Путь | Описание |
|---|---|---|
| GET | `/health` | проверка живости сервера |
| POST | `/analyze/text` | анализ текста конкурента |
| POST | `/analyze/image` | анализ изображения (баннер, лендинг) |
| POST | `/parse/demo` | Selenium-парсинг URL + автоанализ |
| GET | `/history` | последние операции |
| DELETE | `/history` | очистка истории |

## Известные ограничения

- Selenium-парсинг D-ID не работает — сайт использует антибот-защиту, блокирующую headless
  Chrome (таймаут рендерера). Synthesia и HeyGen парсятся корректно.
- Telegram-интерфейс отложен на следующую итерацию.

## Настройка окружения

Скопируйте `.env.example` в `.env` и укажите свой ключ:

```
OPENAI_API_KEY=sk-...
```

`.env` в `.gitignore` — ключ никогда не публикуется в репозитории.
