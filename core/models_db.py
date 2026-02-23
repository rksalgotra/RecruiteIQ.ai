from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
from .database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    scores = relationship("CandidateScore", back_populates="job")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    scores = relationship("CandidateScore", back_populates="resume")


class CandidateScore(Base):
    __tablename__ = "candidate_scores"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)

    skill_score = Column(Float, nullable=False)
    embedding_score = Column(Float, nullable=False)
    experience_score = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)
    category = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="scores")
    resume = relationship("Resume", back_populates="scores")