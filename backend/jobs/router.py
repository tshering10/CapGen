import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from .models import JobStatus, ProcessingJob
from .store import create_job, get_job, update_job
from .tasks import transcribe_video_job


router = APIRouter(prefix="/api/jobs", tags=["jobs"])
SUPPORTED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".m4v",
    ".mkv",
    ".avi",
    ".webm",
}


@router.post("/transcription", response_model=ProcessingJob)
def create_transcription_job(
    video: UploadFile = File(...),
    language: str | None = Form(default=None),
) -> ProcessingJob:
    if not video.filename:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A video file is required.")

    suffix = Path(video.filename).suffix.lower()
    if suffix not in SUPPORTED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported video format: {suffix or 'unknown'}",
        )

    storage_directory = Path("temporary_uploads")
    storage_directory.mkdir(parents=True, exist_ok=True)
    job_id = str(uuid.uuid4())
    video_path = storage_directory / f"{job_id}{suffix}"

    with video_path.open("wb") as destination:
        shutil.copyfileobj(video.file, destination)
    video.file.close()

    job = ProcessingJob(id=job_id, status=JobStatus.QUEUED)
    create_job(job)

    task = transcribe_video_job.apply_async(
        args=[job_id, str(video_path), language],
    )
    job = job.model_copy(update={"task_id": task.id})
    update_job(job)
    return job


@router.get("/transcription/{job_id}", response_model=ProcessingJob)
def get_transcription_job(job_id: str) -> ProcessingJob:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Processing job not found")
    return job
