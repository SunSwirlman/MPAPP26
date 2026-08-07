from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.config import settings
from backend.services import openai_service
from backend.services.history_service import history_service
from backend.services.parsing_service import parse_url

app = FastAPI(
    title="Competitor Analysis Assistant",
    description="Мультимодальный AI-ассистент для анализа конкурентов (ниша: цифровые аватары)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class TextAnalysisRequest(BaseModel):
    text: str
    competitor_name: str | None = None


class ParseRequest(BaseModel):
    url: str | None = None


@app.get("/")
def read_index():
    return FileResponse(f"{FRONTEND_DIR}/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze/text")
def analyze_text_endpoint(payload: TextAnalysisRequest):
    try:
        result = openai_service.analyze_text(payload.text)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ошибка анализа текста: {exc}")

    history_service.add_entry(
        operation_type="analyze_text",
        input_summary=(payload.competitor_name or payload.text[:60]),
        result=result,
    )
    return result


@app.post("/analyze/image")
async def analyze_image_endpoint(file: UploadFile = File(...)):
    image_bytes = await file.read()
    try:
        result = openai_service.analyze_image(image_bytes, mime_type=file.content_type or "image/png")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ошибка анализа изображения: {exc}")

    history_service.add_entry(
        operation_type="analyze_image",
        input_summary=file.filename,
        result=result,
    )
    return result


@app.post("/parse/demo")
def parse_demo_endpoint(payload: ParseRequest):
    url = payload.url or next(iter(settings.COMPETITOR_URLS.values()))

    try:
        parsed = parse_url(url)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ошибка парсинга: {exc}")

    analysis = None
    if parsed.get("first_paragraph"):
        try:
            analysis = openai_service.analyze_parsed_content(
                parsed.get("title") or "",
                parsed.get("h1") or "",
                parsed.get("first_paragraph") or "",
            )
        except Exception:
            analysis = None

    result = {**parsed, "analysis": analysis}

    history_service.add_entry(
        operation_type="parse_demo",
        input_summary=url,
        result=result,
    )
    return result


@app.get("/history")
def get_history():
    return history_service.get_all()


@app.delete("/history")
def clear_history():
    history_service.clear()
    return {"status": "cleared"}
