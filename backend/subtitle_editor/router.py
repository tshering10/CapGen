from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from .models import (
    MergeSegmentRequest,
    SegmentTextUpdate,
    SplitSegmentRequest,
    SubtitleDocument,
    SubtitleSegment,
    SubtitleStyle,
    TimestampUpdate,
)
from .service import SubtitleEditorError, SubtitleEditorService


router = APIRouter(prefix="/api/subtitle-editor", tags=["subtitle-editor"])
service = SubtitleEditorService()
documents: dict[str, SubtitleDocument] = {}


@router.post("/documents", response_model=SubtitleDocument)
def create_document(document: SubtitleDocument | None = None) -> SubtitleDocument:
    created = document or SubtitleDocument()
    documents[str(created.id)] = created
    return created


@router.post("/documents/{document_id}/segments", response_model=SubtitleDocument)
def add_segment(
    document_id: str,
    segment: SubtitleSegment,
) -> SubtitleDocument:
    document = documents.get(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subtitle document not found")
    try:
        updated = service.add_segment(document, segment)
        documents[document_id] = updated
        return updated
    except SubtitleEditorError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.patch(
    "/documents/{document_id}/segments/{segment_id}/text",
    response_model=SubtitleDocument,
)
def update_segment_text(
    document_id: str,
    segment_id: UUID,
    update: SegmentTextUpdate,
) -> SubtitleDocument:
    document = documents.get(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subtitle document not found")
    try:
        updated = service.update_text(document, segment_id, update.text)
        documents[document_id] = updated
        return updated
    except SubtitleEditorError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.patch(
    "/documents/{document_id}/segments/{segment_id}/timestamps",
    response_model=SubtitleDocument,
)
def update_segment_timestamps(
    document_id: str,
    segment_id: UUID,
    update: TimestampUpdate,
) -> SubtitleDocument:
    document = documents.get(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subtitle document not found")
    try:
        updated = service.update_timestamps(document, segment_id, update)
        documents[document_id] = updated
        return updated
    except SubtitleEditorError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.delete(
    "/documents/{document_id}/segments/{segment_id}",
    response_model=SubtitleDocument,
)
def delete_segment(
    document_id: str,
    segment_id: UUID,
) -> SubtitleDocument:
    document = documents.get(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subtitle document not found")
    try:
        updated = service.delete_segment(document, segment_id)
        documents[document_id] = updated
        return updated
    except SubtitleEditorError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.post(
    "/documents/{document_id}/segments/{segment_id}/split",
    response_model=SubtitleDocument,
)
def split_segment(
    document_id: str,
    segment_id: UUID,
    request: SplitSegmentRequest,
) -> SubtitleDocument:
    document = documents.get(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subtitle document not found")
    try:
        updated = service.split_segment(document, segment_id, request)
        documents[document_id] = updated
        return updated
    except SubtitleEditorError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.post(
    "/documents/{document_id}/segments/{segment_id}/merge",
    response_model=SubtitleDocument,
)
def merge_segment(
    document_id: str,
    segment_id: UUID,
    request: MergeSegmentRequest,
) -> SubtitleDocument:
    document = documents.get(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subtitle document not found")
    try:
        updated = service.merge_segments(document, segment_id, request)
        documents[document_id] = updated
        return updated
    except SubtitleEditorError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.put(
    "/documents/{document_id}/style",
    response_model=SubtitleDocument,
)
def update_style(
    document_id: str,
    style: SubtitleStyle,
) -> SubtitleDocument:
    document = documents.get(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subtitle document not found")
    updated = service.update_style(document, style)
    documents[document_id] = updated
    return updated
