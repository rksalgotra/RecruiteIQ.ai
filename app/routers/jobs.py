# app/routers/jobs.py

import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.schemas.job import CreateJobRequest, JobResponse
from app.schemas.base import StandardResponse, Meta
from app.services.job_service import JobService


router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs"])


@router.post("", response_model=StandardResponse)
def create_job(job_data: CreateJobRequest, db: Session = Depends(get_db)):

    request_id = str(uuid.uuid4())
    start_time = datetime.utcnow()

    job = JobService.create_job(db, job_data)

    response_data = {
        "job_id": str(job.id),
        "external_job_id": job.external_job_id,
        "title": job.title,
        "status": job.status,
        "total_applications": job.total_applications,
        "shortlisted_count": job.shortlisted_count,
        "created_at": job.created_at.isoformat()
    }

    return StandardResponse(
        request_id=request_id,
        status="success",
        data=response_data,
        error=None,
        meta=Meta(
            timestamp=datetime.utcnow(),
            processing_time_ms=(datetime.utcnow() - start_time).microseconds // 1000
        )
    )