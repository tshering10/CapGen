import os

import redis

from .models import ProcessingJob


redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
job_store = os.getenv(
    "CAPGEN_JOB_STORE",
    "redis" if os.getenv("REDIS_URL") else "memory",
)
redis_client = (
    redis.Redis.from_url(redis_url, decode_responses=True)
    if job_store == "redis"
    else None
)
memory_jobs: dict[str, ProcessingJob] = {}


def create_job(job: ProcessingJob) -> None:
    if redis_client is None:
        memory_jobs[job.id] = job
        return
    redis_client.set(f"capgen:job:{job.id}", job.model_dump_json())


def get_job(job_id: str) -> ProcessingJob | None:
    if redis_client is None:
        return memory_jobs.get(job_id)
    value = redis_client.get(f"capgen:job:{job_id}")
    if value is None:
        return None
    return ProcessingJob.model_validate_json(value)


def update_job(job: ProcessingJob) -> None:
    if redis_client is None:
        memory_jobs[job.id] = job
        return
    redis_client.set(f"capgen:job:{job.id}", job.model_dump_json())
