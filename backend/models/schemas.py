from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Текст конкурента для анализа")
    competitor_name: Optional[str] = None


class CompetitionAnalysis(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    unique_offers: List[str]
    recommendations: List[str]
    summary: str


class ImageAnalysis(BaseModel):
    description: str
    marketing_insights: List[str]
    visual_style_score: int = Field(..., ge=0, le=10)
    visual_style_analysis: str
    recommendations: List[str]
    design_score: int = Field(..., ge=0, le=10, description="Оценка дизайна под нишу цифровых аватаров")
    animation_potential: str = Field(..., description="Потенциал анимации/оживления материала")


class ParsingResult(BaseModel):
    url: str
    title: Optional[str] = None
    h1: Optional[str] = None
    first_paragraph: Optional[str] = None
    analysis: Optional[CompetitionAnalysis] = None


class DialogueHistoryEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    operation_type: str
    input_summary: str
    result: dict


class DialogueHistory(BaseModel):
    entries: List[DialogueHistoryEntry] = Field(default_factory=list)
