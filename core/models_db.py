# core/models_db.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


# ============================================================
# RESUME TABLE
# ============================================================

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String, nullable=False)
    raw_text = Column(String, nullable=False)
    embedding = Column(JSON, nullable=False)

    skills = relationship("ResumeSkill", back_populates="resume")
    applications = relationship("Application", back_populates="resume")


# ============================================================
# JOB TABLE
# ============================================================

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    embedding = Column(JSON, nullable=False)

    skills = relationship("JobSkill", back_populates="job")
    applications = relationship("Application", back_populates="job")


# ============================================================
# SKILL TABLE
# ============================================================

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)


# ============================================================
# JOB SKILLS
# ============================================================

class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))

    job = relationship("Job", back_populates="skills")


# ============================================================
# RESUME SKILLS
# ============================================================

class ResumeSkill(Base):
    __tablename__ = "resume_skills"

    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))

    resume = relationship("Resume", back_populates="skills")


# ============================================================
# APPLICATION TABLE (CRITICAL FIX)
# ============================================================

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)

    applied_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")


# ============================================================
# CANDIDATE SCORE TABLE
# ============================================================

class CandidateScore(Base):
    __tablename__ = "candidate_scores"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(Integer, ForeignKey("jobs.id"))
    resume_id = Column(Integer, ForeignKey("resumes.id"))

    skill_score = Column(Float)
    embedding_score = Column(Float)
    experience_score = Column(Float)
    final_score = Column(Float)

    category = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())