# core/models.py

from pydantic import BaseModel
from typing import List
from dataclasses import dataclass
from typing import List


class ResumeProfile(BaseModel):
    name: str
    raw_text: str
    skills: List[str]
    years_experience: float


class JobDescription(BaseModel):
    raw_text: str
    required_skills: List[str]
    min_experience: float


class CandidateScore(BaseModel):
    candidate_name: str
    skill_match_score: float
    embedding_score: float
    experience_score: float
    final_score: float
    category: str
    matched_skills: List[str]
    missing_skills: List[str]
    confidence_score: float

    explanation: str | None = None

class ResumeInput(BaseModel):
    name: str
    text: str


class AnalyzeRequest(BaseModel):
    jd_text: str
    resumes: List[ResumeInput]
    use_explanation: bool = False
    top_n: int = 5
    skill_weight: float = 0.35
    embedding_weight: float = 0.35
    experience_weight: float = 0.30


@dataclass
class Candidate:
    name: str
    skills: List[str]
    resume_text: str
    embedding_score: float = 0.0
    experience_score: float = 0.0


@dataclass
class CandidateResult:
    name: str
    skill_match_score: float
    embedding_score: float
    experience_score: float
    final_score: float
    category: str
    matched_skills: List[str]
    missing_skills: List[str]