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
from .store import (
    create_document as store_create_document,
    get_document,
    update_document,
)


router = APIRouter(prefix="/api/subtitle-editor", tags=["subtitle-editor"])
service = SubtitleEditorService()


@router.post("/documents", response_model=SubtitleDocument)
def create_document(document: SubtitleDocument | None = None) -> SubtitleDocument:
    created = document or SubtitleDocument()
    store_create_document(created)
    return created


@router.get("/documents/{document_id}", response_model=SubtitleDocument)
def retrieve_document(document_id: str) -> SubtitleDocument:
    document = get_document(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subtitle document not found")
    return document


@router.post("/documents/{document_id}/segments", response_model=SubtitleDocument)
def add_segment(
    document_id: str,
    segment: SubtitleSegment,
) -> SubtitleDocument:
    document = get_document(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subtitle document not found")
    try:
        updated = service.add_segment(document, segment)
        update_document(updated)
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
    document = get_document(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subtitle document not found")
    try:
        updated = service.update_text(document, segment_id, update.text)
        update_document(updated)
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
    document = get_document(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subtitle document not found")
    try:
        updated = service.update_timestamps(document, segment_id, update)
        update_document(updated)
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
    document = get_document(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subtitle document not found")
    try:
        updated = service.delete_segment(document, segment_id)
        update_document(updated)
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
    document = get_document(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subtitle document not found")
    try:
        updated = service.split_segment(document, segment_id, request)
        update_document(updated)
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
    document = get_document(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subtitle document not found")
    try:
        updated = service.merge_segments(document, segment_id, request)
        update_document(updated)
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
    document = get_document(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subtitle document not found")
    updated = service.update_style(document, style)
    update_document(updated)
    return updated
