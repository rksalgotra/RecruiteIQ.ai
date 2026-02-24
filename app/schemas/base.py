# schemas/base.py

from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class Meta(BaseModel):
    api_version: str = "v1"
    timestamp: datetime
    processing_time_ms: Optional[int] = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    field_errors: Optional[list] = None


class StandardResponse(BaseModel):
    request_id: str
    status: str  # success | error
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None
    meta: Meta