from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    ForeignKey,
    DateTime,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
from .database import Base


# ============================================================
# SKILL MASTER TABLE
# ============================================================

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    normalized_name = Column(String, nullable=False, unique=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    resumes = relationship("ResumeSkill", back_populates="skill", cascade="all, delete")
    jobs = relationship("JobSkill", back_populates="skill", cascade="all, delete")


# ============================================================
# JOB TABLE
# ============================================================

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    scores = relationship("CandidateScore", back_populates="job", cascade="all, delete")
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete")


# ============================================================
# RESUME TABLE
# ============================================================

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    scores = relationship("CandidateScore", back_populates="resume", cascade="all, delete")
    skills = relationship("ResumeSkill", back_populates="resume", cascade="all, delete")


# ============================================================
# JOB ↔ SKILL MAPPING (Many-to-Many)
# ============================================================

class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("job_id", "skill_id", name="unique_job_skill"),
    )

    # Relationships
    job = relationship("Job", back_populates="skills")
    skill = relationship("Skill", back_populates="jobs")


# ============================================================
# RESUME ↔ SKILL MAPPING (Many-to-Many)
# ============================================================

class ResumeSkill(Base):
    __tablename__ = "resume_skills"

    id = Column(Integer, primary_key=True, index=True)

    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("resume_id", "skill_id", name="unique_resume_skill"),
    )

    # Relationships
    resume = relationship("Resume", back_populates="skills")
    skill = relationship("Skill", back_populates="resumes")


# ============================================================
# CANDIDATE SCORE TABLE
# ============================================================

class CandidateScore(Base):
    __tablename__ = "candidate_scores"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)

    skill_score = Column(Float, nullable=False)
    embedding_score = Column(Float, nullable=False)
    experience_score = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)
    category = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("job_id", "resume_id", name="unique_job_resume_score"),
    )

    # Relationships
    job = relationship("Job", back_populates="scores")
    resume = relationship("Resume", back_populates="scores")