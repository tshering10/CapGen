from jobs.models import JobStatus, ProcessingJob
from jobs.store import create_job, get_job, update_job


def test_processing_job_status():
    job = ProcessingJob(id="test-job", status=JobStatus.QUEUED)
    create_job(job)

    stored = get_job("test-job")
    assert stored is not None
    assert stored.status == JobStatus.QUEUED
    assert stored.document_id is None

    updated = stored.model_copy(update={"status": JobStatus.COMPLETED})
    update_job(updated)

    assert get_job("test-job").status == JobStatus.COMPLETED
