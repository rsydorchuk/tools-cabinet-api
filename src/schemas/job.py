import uuid
from datetime import datetime

from pydantic import BaseModel


class UploadRequest(BaseModel):
    filename: str
    content_type: str
    tool: str
    from_format: str
    to_format: str


class UploadResponse(BaseModel):
    job_id: uuid.UUID
    upload_url: str
    expires_at: datetime


class JobStatus(BaseModel):
    job_id: uuid.UUID
    status: str
    output_url: str | None = None
    error: str | None = None
