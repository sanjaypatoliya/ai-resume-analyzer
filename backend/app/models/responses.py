from datetime import datetime

from pydantic import BaseModel


class UploadResponse(BaseModel):
    upload_url: str
    upload_fields: dict  # presigned POST signature fields
    s3_key: str
    expires_in: int


class CategoryScore(BaseModel):
    name: str
    score: int
    rationale: str


class ExperienceItem(BaseModel):
    title: str
    company: str
    duration: str


class EducationItem(BaseModel):
    degree: str
    institution: str
    year: str


class AnalysisResult(BaseModel):
    id: str
    overall_score: int
    categories: list[CategoryScore]
    skills: list[str]
    experience: list[ExperienceItem]
    education: list[EducationItem]
    suggestions: list[str]
    created_at: datetime
    file_name: str
    job_description: str


class HistoryItem(BaseModel):
    id: str
    file_name: str
    overall_score: int
    created_at: datetime


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int
