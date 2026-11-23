from enum import Enum

from pydantic import BaseModel


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingJob(BaseModel):
    id: str
    status: JobStatus
    document_id: str | None = None
    task_id: str | None = None
    error: str | None = None
