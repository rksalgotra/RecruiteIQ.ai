# app/db/models.py

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Integer,
    Enum,
    ForeignKey,
    Index,
    JSON,
    DateTime,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
from app.schemas.common import JobStatus, ApplicationStatus

class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    external_job_id = Column(String, unique=True, nullable=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    location_type = Column(String, nullable=False)
    country = Column(String, nullable=False)
    city = Column(String, nullable=True)

    employment_type = Column(String, nullable=False)
    experience_level = Column(String, nullable=False)

    required_skills = Column(JSON, nullable=False)
    nice_to_have_skills = Column(JSON, nullable=True)

    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    currency = Column(String, nullable=True)

    status = Column(Enum(JobStatus), default=JobStatus.draft, index=True)

    embedding_vector = Column(JSON, nullable=True)
    embedding_status = Column(String, default="pending")

    total_applications = Column(Integer, default=0)
    shortlisted_count = Column(Integer, default=0)

    # Relationships
    screening_questions = relationship(
        "ScreeningQuestion",
        back_populates="job",
        cascade="all, delete-orphan"
    )

    applications = relationship(
        "Application",
        back_populates="job",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_job_status", "status"),
        Index("idx_job_created_at", "created_at"),
    )

class ScreeningQuestion(Base, TimestampMixin):
    __tablename__ = "screening_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)

    question_key = Column(String, nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)
    required = Column(String, default=True)

    job = relationship("Job", back_populates="screening_questions")

    __table_args__ = (
        Index("idx_screening_job_id", "job_id"),
    )
class Candidate(Base, TimestampMixin):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    external_candidate_id = Column(String, unique=True, nullable=True)

    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=True)
    name = Column(String, nullable=True)

    resume_path = Column(String, nullable=True)
    resume_hash = Column(String, nullable=True, index=True)

    parsed_resume_json = Column(JSON, nullable=True)
    embedding_vector = Column(JSON, nullable=True)

    years_experience = Column(Float, nullable=True)
    current_location = Column(String, nullable=True)

    source = Column(String, nullable=True)
    status = Column(String, default="active", index=True)

    applications = relationship(
        "Application",
        back_populates="candidate",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_candidate_email", "email"),
        Index("idx_candidate_resume_hash", "resume_hash"),
    )

class Application(Base, TimestampMixin):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)

    cover_letter = Column(Text, nullable=True)

    screening_answers = Column(JSON, nullable=True)
    screening_score = Column(Float, nullable=True)

    ai_score = Column(Float, nullable=True)
    score_breakdown = Column(JSON, nullable=True)

    ranking_position = Column(Integer, nullable=True)

    shortlist_recommendation = Column(String, default=False)

    status = Column(
        Enum(ApplicationStatus),
        default=ApplicationStatus.applied,
        index=True
    )

    applied_at = Column(DateTime, default=datetime.utcnow)
    last_scored_at = Column(DateTime, nullable=True)

    job = relationship("Job", back_populates="applications")
    candidate = relationship("Candidate", back_populates="applications")

    __table_args__ = (
        UniqueConstraint("job_id", "candidate_id", name="uq_job_candidate"),
        Index("idx_job_score", "job_id", "ai_score"),
        Index("idx_job_status", "job_id", "status"),
    )