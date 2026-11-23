import shutil
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from .audio import AudioExtractionError, extract_audio
from .models import TranscriptionResult
from .service import TranscriptionError, TranscriptionService


router = APIRouter(prefix="/api/transcription", tags=["transcription"])
transcription_service = TranscriptionService()

SUPPORTED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".m4v",
    ".mkv",
    ".avi",
    ".webm",
}


@router.post("/transcribe", response_model=TranscriptionResult)
def transcribe_video(
    video: UploadFile = File(...),
    language: str | None = Form(default=None),
) -> TranscriptionResult:
    if not video.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A video file is required.",
        )

    extension = Path(video.filename).suffix.lower()
    if extension not in SUPPORTED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported video format: {extension or 'unknown'}",
        )

    temporary_directory = tempfile.TemporaryDirectory(
        prefix="capgen_upload_"
    )
    upload_path = Path(temporary_directory.name) / (
        f"{uuid.uuid4().hex}{extension}"
    )
    audio_path: Path | None = None

    try:
        with upload_path.open("wb") as destination:
            shutil.copyfileobj(video.file, destination)

        audio_path = extract_audio(upload_path)
        return transcription_service.transcribe(audio_path, language)
    except AudioExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except TranscriptionError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    finally:
        video.file.close()
        temporary_directory.cleanup()
        if audio_path is not None:
            audio_directory = getattr(
                audio_path,
                "_capgen_temp_directory",
                None,
            )
            if audio_directory is not None:
                audio_directory.cleanup()
