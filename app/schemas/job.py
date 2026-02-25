from pydantic import BaseModel
from typing import List


class LocationSchema(BaseModel):
    type: str
    country: str
    city: str


class SalaryRangeSchema(BaseModel):
    min: int
    max: int
    currency: str


class ScreeningQuestionSchema(BaseModel):
    id: str
    type: str
    question: str
    required: bool


class JobCreateSchema(BaseModel):
    external_job_id: str
    title: str
    description: str
    location: LocationSchema
    employment_type: str
    experience_level: str
    required_skills: List[str]
    nice_to_have_skills: List[str]
    salary_range: SalaryRangeSchema
    screening_questions: List[ScreeningQuestionSchema]
    status: str