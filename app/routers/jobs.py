from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

from app.models.job import Job, ScreeningQuestion
from app.schemas.job import JobCreateSchema

router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs"])


@router.post("")
def create_job(payload: JobCreateSchema, db: Session = Depends(get_db)):

    job = Job(
        external_job_id=payload.external_job_id,
        title=payload.title,
        description=payload.description,
        employment_type=payload.employment_type,
        experience_level=payload.experience_level,
        status=payload.status,
        location_type=payload.location.type,
        location_country=payload.location.country,
        location_city=payload.location.city,
        salary_min=payload.salary_range.min,
        salary_max=payload.salary_range.max,
        salary_currency=payload.salary_range.currency,
    )

    # Nested screening questions
    for q in payload.screening_questions:
        question = ScreeningQuestion(
            id=q.id,
            type=q.type,
            question=q.question,
            required=q.required
        )
        job.screening_questions.append(question)

    db.add(job)
    db.commit()
    db.refresh(job)

    return {"message": "Job created successfully", "job_id": job.id}