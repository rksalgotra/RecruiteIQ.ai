# app/repositories/job_repository.py

from sqlalchemy.orm import Session
from app.db.models import Job, ScreeningQuestion
from app.schemas.job import CreateJobRequest


class JobRepository:

    @staticmethod
    def create_job(db: Session, job_data: CreateJobRequest) -> Job:
        job = Job(
            external_job_id=job_data.external_job_id,
            title=job_data.title,
            description=job_data.description,
            location_type=job_data.location.type,
            country=job_data.location.country,
            city=job_data.location.city,
            employment_type=job_data.employment_type,
            experience_level=job_data.experience_level,
            required_skills=job_data.required_skills,
            nice_to_have_skills=job_data.nice_to_have_skills,
            salary_min=job_data.salary_range.min if job_data.salary_range else None,
            salary_max=job_data.salary_range.max if job_data.salary_range else None,
            currency=job_data.salary_range.currency if job_data.salary_range else None,
            status=job_data.status
        )

        db.add(job)
        db.flush()  # get job.id before commit

        # Add screening questions
        for q in job_data.screening_questions:
            question = ScreeningQuestion(
                job_id=job.id,
                question_key=q.id,
                question_text=q.question,
                question_type=q.type,
                required=q.required
            )
            db.add(question)

        db.commit()
        db.refresh(job)

        return job