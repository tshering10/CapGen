from pathlib import Path

from .celery_app import celery_app
from .models import JobStatus
from .store import get_job, update_job


@celery_app.task(bind=True)
def transcribe_video_job(
    self,
    job_id: str,
    video_path: str,
    language: str | None = None,
):
    from subtitle_editor.models import SubtitleDocument, SubtitleSegment
    from subtitle_editor.store import create_document
    from transcription.audio import cleanup_extracted_audio, extract_audio
    from transcription.service import TranscriptionService

    job = get_job(job_id)
    if job is None:
        raise RuntimeError(f"Processing job not found: {job_id}")
    update_job(job.model_copy(
        update={
            "status": JobStatus.PROCESSING,
            "task_id": self.request.id,
        }
    ))

    audio_path = None
    try:
        audio_path = extract_audio(Path(video_path))
        result = TranscriptionService().transcribe(audio_path, language)

        segments = [
            SubtitleSegment(
                start=segment.start,
                end=segment.end,
                text=segment.text,
            )
            for segment in result.segments
        ]
        document = SubtitleDocument(segments=segments)
        create_document(document)

        update_job(job.model_copy(
            update={
                "status": JobStatus.COMPLETED,
                "document_id": str(document.id),
                "task_id": self.request.id,
            }
        ))
        Path(video_path).unlink(missing_ok=True)
        return {"document_id": str(document.id)}
    except Exception as exc:
        update_job(job.model_copy(
            update={
                "status": JobStatus.FAILED,
                "task_id": self.request.id,
                "error": str(exc),
            }
        ))
        Path(video_path).unlink(missing_ok=True)
        raise
    finally:
        if audio_path is not None:
            cleanup_extracted_audio(audio_path)
