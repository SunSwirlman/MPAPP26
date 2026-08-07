import base64
import json

from openai import OpenAI

from backend.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

TEXT_ANALYSIS_PROMPT = """Ты — эксперт по конкурентному анализу. Проанализируй предоставленный текст конкурента и верни структурированный JSON-ответ.

Формат ответа (строго JSON):
{
  "strengths": ["сильная сторона 1", "сильная сторона 2", ...],
  "weaknesses": ["слабая сторона 1", "слабая сторона 2", ...],
  "unique_offers": ["уникальное предложение 1", "уникальное предложение 2", ...],
  "recommendations": ["рекомендация 1", "рекомендация 2", ...],
  "summary": "Краткое резюме анализа"
}

Важно:
- Каждый массив должен содержать 3-5 пунктов
- Пиши на русском языке
- Будь конкретен и практичен в рекомендациях"""

IMAGE_ANALYSIS_PROMPT = """Ты — эксперт по визуальному маркетингу и дизайну в нише "Персональные цифровые аватары"
(AI-видео с говорящими аватарами, digital humans). Проанализируй изображение конкурента (баннер,
лендинг, превью продукта) и верни структурированный JSON:

{
  "description": "Детальное описание того, что изображено",
  "marketing_insights": ["инсайт 1", "инсайт 2", ...],
  "visual_style_score": 7,
  "visual_style_analysis": "Анализ визуального стиля конкурента",
  "recommendations": ["рекомендация 1", "рекомендация 2", ...],
  "design_score": 8,
  "animation_potential": "Оценка потенциала оживления/анимации этого материала для нашей ниши цифровых аватаров"
}

Важно:
- visual_style_score и design_score — от 0 до 10
- Каждый массив должен содержать 3-5 пунктов
- Пиши на русском языке
- Оценивай: цветовую палитру, типографику, композицию, UX/UI элементы
- animation_potential: конкретно опиши, как этот материал можно было бы "оживить" через AI-аватара
  (например: подошёл бы говорящий аватар поверх баннера, потенциал для видео-версии и т.д.)"""


def _extract_json(content: str) -> dict:
    return json.loads(content)


def analyze_text(text: str) -> dict:
    """Анализ текстового описания конкурента."""
    completion = client.chat.completions.create(
        model=settings.TEXT_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": TEXT_ANALYSIS_PROMPT},
            {"role": "user", "content": text},
        ],
    )
    return _extract_json(completion.choices[0].message.content)


def analyze_image(image_bytes: bytes, mime_type: str = "image/png") -> dict:
    """Анализ изображения конкурента (баннер, лендинг, карточка товара)."""
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    completion = client.chat.completions.create(
        model=settings.VISION_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": IMAGE_ANALYSIS_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{image_b64}"},
                    },
                ],
            }
        ],
    )
    return _extract_json(completion.choices[0].message.content)


def analyze_parsed_content(title: str, h1: str, first_paragraph: str) -> dict:
    """Анализ распарсенного контента сайта конкурента (title + h1 + первый абзац)."""
    combined = f"Title: {title}\nH1: {h1}\nТекст: {first_paragraph}"
    return analyze_text(combined)
