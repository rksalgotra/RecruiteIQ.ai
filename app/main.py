import uuid
import time
import logging
from typing import Callable, List

from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import delete

from core.embedding_service import generate_embedding
from core.database import get_db
from core.models_db import (
    Resume,
    CandidateScore,
    Job,
    JobSkill,
    ResumeSkill,
)
from core.vector_search import find_similar_resumes
from core.skill_service import extract_skills_from_text


# ============================================================
# App Initialization
# ============================================================

app = FastAPI(title="TalentAIQ - Enterprise Edition", version="3.0.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("talentaiq")


# ============================================================
# API MODELS
# ============================================================

class MatchRequest(BaseModel):
    candidate_name: str
    skills: List[str]
    experience_years: int


class ResumeStoreResponse(BaseModel):
    candidate_name: str
    rule_score: float
    vector_score: float
    hybrid_score: float
    category: str
    explanation: str


class JobCreateRequest(BaseModel):
    title: str
    description: str


class JobResponse(BaseModel):
    job_id: int
    title: str


class RankedCandidate(BaseModel):
    resume_id: int
    candidate_name: str
    embedding_score: float
    rule_score: float
    hybrid_score: float
    category: str


# ============================================================
# MATCH ENDPOINT (Resume Creation)
# ============================================================

@app.post("/api/v1/resume", response_model=ResumeStoreResponse)
async def match_candidate(payload: MatchRequest, db: Session = Depends(get_db)):

    resume_text = (
        f"{payload.candidate_name}. "
        f"Skills: {', '.join(payload.skills)}. "
        f"Experience: {payload.experience_years} years."
    )

    embedding = generate_embedding(resume_text)

    resume = Resume(
        candidate_name=payload.candidate_name,
        raw_text=resume_text,
        embedding=embedding,
    )

    db.add(resume)
    db.flush()

    # 🔥 Structured Skill Mapping
    matched_skills = extract_skills_from_text(resume_text, db)
    for skill in matched_skills:
        db.add(ResumeSkill(resume_id=resume.id, skill_id=skill.id))

    db.commit()

    return MatchResponse(
        candidate_name=payload.candidate_name,
        rule_score=0.0,
        vector_score=0.0,
        hybrid_score=0.0,
        category="Resume Stored",
        explanation="Resume successfully stored with structured skills.",
    )


# ============================================================
# JOB CREATION
# ============================================================

@app.post("/api/v1/job", response_model=JobResponse)
async def create_job(payload: JobCreateRequest, db: Session = Depends(get_db)):

    job_text = f"{payload.title}. {payload.description}"
    embedding = generate_embedding(job_text)

    job = Job(
        title=payload.title,
        description=payload.description,
        embedding=embedding,
    )

    db.add(job)
    db.flush()

    # 🔥 Structured Skill Mapping
    matched_skills = extract_skills_from_text(job_text, db)
    for skill in matched_skills:
        db.add(JobSkill(job_id=job.id, skill_id=skill.id))

    db.commit()

    return JobResponse(job_id=job.id, title=job.title)


# ============================================================
# JOB RANKING (Hybrid Intelligence)
# ============================================================

@app.get("/api/v1/job/{job_id}/rank", response_model=List[RankedCandidate])
async def rank_candidates_for_job(job_id: int, db: Session = Depends(get_db)):

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resumes = db.query(Resume).all()
    if not resumes:
        return []

    # Remove previous scores for this job
    db.execute(delete(CandidateScore).where(CandidateScore.job_id == job_id))
    db.commit()

    # 🔥 Get similarity results
    similarity_results = find_similar_resumes(db, job.embedding, limit=10000)

    if not similarity_results:
        return []

    # 🔥 Normalize embedding scores
    raw_scores = [row[2] for row in similarity_results]
    max_score = max(raw_scores)
    min_score = min(raw_scores)

    def normalize(score):
        if max_score == min_score:
            return 1.0
        return (score - min_score) / (max_score - min_score)

    similarity_map = {row[0]: normalize(row[2]) for row in similarity_results}

    # 🔥 Get job skills
    job_skill_ids = {
        js.skill_id
        for js in db.query(JobSkill).filter(JobSkill.job_id == job_id).all()
    }

    ranked: List[RankedCandidate] = []

    for resume in resumes:

        embedding_score = round(float(similarity_map.get(resume.id, 0.0)), 3)

        resume_skill_ids = {
            rs.skill_id
            for rs in db.query(ResumeSkill).filter(
                ResumeSkill.resume_id == resume.id
            ).all()
        }

        if not job_skill_ids:
            skill_score = 0.0
        else:
            overlap = job_skill_ids.intersection(resume_skill_ids)
            skill_score = round(len(overlap) / len(job_skill_ids), 3)

        # 🔥 Balanced hybrid
        hybrid_score = round(
            (0.5 * embedding_score) + (0.5 * skill_score),
            3
        )

        category = (
            "Strong Match" if hybrid_score >= 0.7 else
            "Moderate Match" if hybrid_score >= 0.4 else
            "Weak Match"
        )

        db.add(CandidateScore(
            job_id=job_id,
            resume_id=resume.id,
            skill_score=skill_score,
            embedding_score=embedding_score,
            experience_score=0.0,
            final_score=hybrid_score,
            category=category,
        ))

        ranked.append(
            RankedCandidate(
                resume_id=resume.id,
                candidate_name=resume.candidate_name,
                embedding_score=embedding_score,
                rule_score=skill_score,
                hybrid_score=hybrid_score,
                category=category,
            )
        )

    db.commit()

    ranked.sort(key=lambda x: x.hybrid_score, reverse=True)

    return ranked