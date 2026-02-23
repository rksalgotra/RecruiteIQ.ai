import time
import logging
import hashlib
from typing import List

from prometheus_client import Counter, Histogram
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import delete

from core.embedding_service import generate_embedding
from core.database import get_db
from core.models_db import (
    Resume,
    CandidateScore,
    Job,
    JobSkill,
    ResumeSkill,
    Application,   # ✅ NEW
)
from core.vector_search import find_similar_resumes
from core.skill_service import extract_skills_from_text


# ============================================================
# App Initialization
# ============================================================

app = FastAPI(title="TalentAIQ - Enterprise Edition", version="3.2.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("talentaiq")


# ============================================================
# METRICS
# ============================================================

resume_ingestion_counter = Counter(
    "resume_ingested_total",
    "Total number of resumes ingested"
)

embedding_latency_histogram = Histogram(
    "embedding_generation_seconds",
    "Time spent generating embeddings"
)

resume_request_latency = Histogram(
    "resume_request_seconds",
    "Total resume ingestion request time"
)


# ============================================================
# API MODELS
# ============================================================

class ResumeCreateRequest(BaseModel):
    candidate_name: str
    skills: List[str]
    experience_years: int


class ResumeStoreResponse(BaseModel):
    resume_id: int
    candidate_name: str
    category: str
    explanation: str


class JobCreateRequest(BaseModel):
    title: str
    description: str


class JobResponse(BaseModel):
    job_id: int
    title: str


class ApplyRequest(BaseModel):
    resume_id: int


class RankedCandidate(BaseModel):
    resume_id: int
    candidate_name: str
    embedding_score: float
    rule_score: float
    hybrid_score: float
    category: str


# ============================================================
# RESUME INGESTION
# ============================================================

@app.post("/api/v1/resume", response_model=ResumeStoreResponse)
async def store_resume(payload: ResumeCreateRequest, db: Session = Depends(get_db)):

    request_start = time.time()

    resume_text = (
        f"{payload.candidate_name}. "
        f"Skills: {', '.join(payload.skills)}. "
        f"Experience: {payload.experience_years} years."
    )

    resume_hash = hashlib.sha256(resume_text.encode()).hexdigest()

    existing_resume = db.query(Resume).filter(
        Resume.raw_text == resume_text
    ).first()

    if existing_resume:
        return ResumeStoreResponse(
            resume_id=existing_resume.id,
            candidate_name=existing_resume.candidate_name,
            category="Duplicate Resume",
            explanation="Resume already exists in system.",
        )

    embed_start = time.time()
    embedding = generate_embedding(resume_text)
    embedding_latency_histogram.observe(time.time() - embed_start)

    resume = Resume(
        candidate_name=payload.candidate_name,
        raw_text=resume_text,
        embedding=embedding,
    )

    db.add(resume)
    db.flush()

    matched_skills = extract_skills_from_text(resume_text, db)
    for skill in matched_skills:
        db.add(ResumeSkill(resume_id=resume.id, skill_id=skill.id))

    db.commit()

    resume_ingestion_counter.inc()
    resume_request_latency.observe(time.time() - request_start)

    return ResumeStoreResponse(
        resume_id=resume.id,
        candidate_name=payload.candidate_name,
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

    matched_skills = extract_skills_from_text(job_text, db)
    for skill in matched_skills:
        db.add(JobSkill(job_id=job.id, skill_id=skill.id))

    db.commit()

    return JobResponse(job_id=job.id, title=job.title)


# ============================================================
# APPLY TO JOB (NEW)
# ============================================================

@app.post("/api/v1/job/{job_id}/apply")
async def apply_to_job(job_id: int, payload: ApplyRequest, db: Session = Depends(get_db)):

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resume = db.query(Resume).filter(Resume.id == payload.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    existing = db.query(Application).filter(
        Application.job_id == job_id,
        Application.resume_id == payload.resume_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Resume already applied to this job"
        )

    db.add(Application(
        job_id=job_id,
        resume_id=payload.resume_id
    ))

    db.commit()

    return {"message": "Application submitted successfully"}


# ============================================================
# JOB RANKING (Applicants Only + Optimized)
# ============================================================

@app.get("/api/v1/job/{job_id}/rank", response_model=List[RankedCandidate])
async def rank_candidates_for_job(job_id: int, db: Session = Depends(get_db)):

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # ✅ Fetch only applied resumes (optimized join)
    applications = db.query(Application).options(
        joinedload(Application.resume)
    ).filter(
        Application.job_id == job_id
    ).all()

    if not applications:
        return []

    resumes = [app.resume for app in applications]

    db.execute(delete(CandidateScore).where(CandidateScore.job_id == job_id))
    db.commit()

    similarity_results = find_similar_resumes(db, job.embedding, limit=10000)

    raw_scores = [row[2] for row in similarity_results] if similarity_results else []
    max_score = max(raw_scores) if raw_scores else 1
    min_score = min(raw_scores) if raw_scores else 0

    def normalize(score):
        if max_score == min_score:
            return 1.0
        return (score - min_score) / (max_score - min_score)

    similarity_map = {
        row[0]: normalize(row[2])
        for row in similarity_results
    }

    job_skill_ids = {
        js.skill_id
        for js in db.query(JobSkill).filter(
            JobSkill.job_id == job_id
        ).all()
    }

    ranked: List[RankedCandidate] = []

    for resume in resumes:

        embedding_score = round(
            float(similarity_map.get(resume.id, 0.0)),
            3
        )

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
            skill_score = round(
                len(overlap) / len(job_skill_ids),
                3
            )

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