# schemas/job.py

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum
from .common import JobStatus


# =========================
# Enums
# =========================

class LocationType(str, Enum):
    remote = "remote"
    onsite = "onsite"
    hybrid = "hybrid"


class EmploymentType(str, Enum):
    full_time = "full_time"
    contract = "contract"
    internship = "internship"


class ExperienceLevel(str, Enum):
    junior = "junior"
    mid = "mid"
    senior = "senior"
    lead = "lead"


# =========================
# Nested Models
# =========================

class SalaryRange(BaseModel):
    min: float = Field(gt=0)
    max: float = Field(gt=0)
    currency: str

    @validator("max")
    def validate_salary(cls, v, values):
        if "min" in values and v <= values["min"]:
            raise ValueError("salary max must be greater than min")
        return v


class Location(BaseModel):
    type: LocationType
    country: str
    city: Optional[str] = None


class ScreeningQuestion(BaseModel):
    id: str
    question: str
    type: str  # number | boolean | text | choice
    required: bool = True


# =========================
# Requests
# =========================

class CreateJobRequest(BaseModel):
    external_job_id: Optional[str]
    title: str
    description: str
    location: Location
    employment_type: EmploymentType
    experience_level: ExperienceLevel
    required_skills: List[str] = Field(min_items=1)
    nice_to_have_skills: Optional[List[str]] = []
    salary_range: Optional[SalaryRange]
    screening_questions: Optional[List[ScreeningQuestion]] = []
    status: Optional[JobStatus] = JobStatus.draft


class UpdateJobRequest(BaseModel):
    title: Optional[str]
    description: Optional[str]
    required_skills: Optional[List[str]]
    nice_to_have_skills: Optional[List[str]]
    salary_range: Optional[SalaryRange]
    location: Optional[Location]
    employment_type: Optional[EmploymentType]
    experience_level: Optional[ExperienceLevel]


class UpdateJobStatusRequest(BaseModel):
    status: JobStatus


# =========================
# Responses
# =========================

class JobStatistics(BaseModel):
    total_applications: int
    shortlisted_count: int
    average_score: Optional[float] = None


class JobResponse(BaseModel):
    job_id: str
    external_job_id: Optional[str]
    title: str
    description: str
    location: Location
    employment_type: EmploymentType
    experience_level: ExperienceLevel
    required_skills: List[str]
    nice_to_have_skills: List[str]
    salary_range: Optional[SalaryRange]
    status: JobStatus
    statistics: JobStatistics
    created_at: str
    updated_at: str


class JobListItemResponse(BaseModel):
    job_id: str
    title: str
    status: JobStatus
    total_applications: int
    shortlisted_count: int
    created_at: str