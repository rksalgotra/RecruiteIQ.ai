# schemas/application.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from .common import ApplicationStatus


# =========================
# Candidate Info
# =========================

class CandidateInfo(BaseModel):
    email: EmailStr
    phone: Optional[str]
    name: Optional[str]


# =========================
# Apply Request
# =========================

class ApplyJobRequest(BaseModel):
    job_id: str
    candidate: CandidateInfo
    cover_letter: Optional[str]
    answers: Optional[Dict[str, object]] = {}


# =========================
# Scoring
# =========================

class ScoreBreakdown(BaseModel):
    skill_match: float = Field(ge=0, le=1)
    experience_match: float = Field(ge=0, le=1)
    screening_match: float = Field(ge=0, le=1)


class ScoreResponse(BaseModel):
    overall: float = Field(ge=0, le=1)
    breakdown: ScoreBreakdown


# =========================
# Responses
# =========================

class ApplicationResponse(BaseModel):
    application_id: str
    job_id: str
    candidate_id: str
    status: ApplicationStatus
    score: ScoreResponse
    ranking_position: Optional[int]
    shortlist_recommendation: bool
    applied_at: str


class ApplicationListItemResponse(BaseModel):
    application_id: str
    candidate_name: Optional[str]
    score: float
    ranking_position: Optional[int]
    status: ApplicationStatus
    applied_at: str


class RecomputeMatchRequest(BaseModel):
    job_id: str
    candidate_id: str
    force_recompute: Optional[bool] = False