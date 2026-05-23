from typing import List, Optional

from pydantic import BaseModel, Field


class StorageMetadata(BaseModel):
    bucket: Optional[str] = None
    object_key: Optional[str] = None
    file_url: Optional[str] = None
    storage_enabled: bool = False


class AnalysisResponse(BaseModel):
    filename: str
    match_score: float = Field(..., ge=0, le=100)
    semantic_similarity: float = Field(..., ge=0, le=100)
    keyword_match_score: float = Field(..., ge=0, le=100)
    skill_match_score: float = Field(..., ge=0, le=100)
    extracted_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    suggestions: List[str]
    storage: StorageMetadata


class UploadResponse(BaseModel):
    filename: str
    storage: StorageMetadata
