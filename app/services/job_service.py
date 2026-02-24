# app/services/job_service.py

from sqlalchemy.orm import Session
from app.repositories.job_repository import JobRepository
from app.schemas.job import CreateJobRequest


class JobService:

    @staticmethod
    def create_job(db: Session, job_data: CreateJobRequest):
        return JobRepository.create_job(db, job_data)