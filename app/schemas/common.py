# schemas/common.py

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# =========================
# Pagination
# =========================

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class PaginatedMeta(BaseModel):
    total: int
    page: int
    limit: int


# =========================
# Sorting
# =========================

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


# =========================
# Status Enums
# =========================

class JobStatus(str, Enum):
    draft = "draft"
    open = "open"
    paused = "paused"
    closed = "closed"
    archived = "archived"


class ApplicationStatus(str, Enum):
    applied = "applied"
    shortlisted = "shortlisted"
    rejected = "rejected"
    withdrawn = "withdrawn"


class CandidateStatus(str, Enum):
    active = "active"
    archived = "archived"