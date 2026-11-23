import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from subtitle_editor.router import documents
from .formats import write_ass, write_srt
from .service import VideoRenderError, render_video


router = APIRouter(prefix="/api/video-renderer", tags=["video-renderer"])


def get_document(document_id: str):
    document = documents.get(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subtitle document not found")
    return document


@router.post("/documents/{document_id}/srt")
def export_srt(document_id: str):
    document = get_document(document_id)
    temporary_directory = tempfile.TemporaryDirectory(prefix="capgen_srt_")
    srt_path = write_srt(
        document,
        Path(temporary_directory.name) / "subtitles.srt",
    )

    return FileResponse(
        srt_path,
        media_type="application/x-subrip",
        filename="subtitles.srt",
        background=BackgroundTask(temporary_directory.cleanup),
    )


@router.post("/documents/{document_id}/render")
def render_document(
    document_id: str,
    video: UploadFile = File(...),
):
    document = get_document(document_id)
    if not video.filename:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A video file is required.")

    suffix = Path(video.filename).suffix.lower()
    if suffix not in {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".webm"}:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported video format: {suffix or 'unknown'}",
        )

    temporary_directory = tempfile.TemporaryDirectory(prefix="capgen_render_")
    upload_path = Path(temporary_directory.name) / f"input{suffix}"
    ass_path = Path(temporary_directory.name) / "subtitles.ass"
    output_path = Path(temporary_directory.name) / "rendered.mp4"

    try:
        with upload_path.open("wb") as destination:
            shutil.copyfileobj(video.file, destination)

        write_ass(document, ass_path)
        render_video(upload_path, output_path, ass_path)

        response = FileResponse(
            output_path,
            media_type="video/mp4",
            filename="rendered.mp4",
            background=BackgroundTask(temporary_directory.cleanup),
        )
        return response
    except VideoRenderError as exc:
        temporary_directory.cleanup()
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    finally:
        video.file.close()
