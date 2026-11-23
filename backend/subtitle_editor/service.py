from copy import deepcopy
from uuid import UUID

from .models import (
    MergeSegmentRequest,
    SplitSegmentRequest,
    SubtitleDocument,
    SubtitleSegment,
    SubtitleStyle,
    TimestampUpdate,
)


class SubtitleEditorError(ValueError):
    pass


class SubtitleEditorService:
    def get_segment(
        self,
        document: SubtitleDocument,
        segment_id: UUID,
    ) -> SubtitleSegment:
        for segment in document.segments:
            if segment.id == segment_id:
                return segment
        raise SubtitleEditorError("Subtitle segment not found")

    def add_segment(
        self,
        document: SubtitleDocument,
        segment: SubtitleSegment,
    ) -> SubtitleDocument:
        updated = deepcopy(document)
        updated.segments.append(segment)
        updated.segments.sort(key=lambda item: item.start)
        return updated

    def update_text(
        self,
        document: SubtitleDocument,
        segment_id: UUID,
        text: str,
    ) -> SubtitleDocument:
        updated = deepcopy(document)
        segment = self.get_segment(updated, segment_id)
        segment.text = text
        return updated

    def update_timestamps(
        self,
        document: SubtitleDocument,
        segment_id: UUID,
        update: TimestampUpdate,
    ) -> SubtitleDocument:
        updated = deepcopy(document)
        segment = self.get_segment(updated, segment_id)
        segment.start = update.start
        segment.end = update.end
        updated.segments.sort(key=lambda item: item.start)
        return updated

    def delete_segment(
        self,
        document: SubtitleDocument,
        segment_id: UUID,
    ) -> SubtitleDocument:
        updated = deepcopy(document)
        segment = self.get_segment(updated, segment_id)
        updated.segments.remove(segment)
        return updated

    def split_segment(
        self,
        document: SubtitleDocument,
        segment_id: UUID,
        request: SplitSegmentRequest,
    ) -> SubtitleDocument:
        updated = deepcopy(document)
        segment = self.get_segment(updated, segment_id)

        if not segment.start < request.timestamp < segment.end:
            raise SubtitleEditorError(
                "Split timestamp must be inside the segment"
            )

        midpoint_text = segment.text.strip()
        words = midpoint_text.split()

        if len(words) > 1:
            split_at = len(words) // 2
            first_text = " ".join(words[:split_at])
            second_text = " ".join(words[split_at:])
        else:
            first_text = midpoint_text
            second_text = midpoint_text

        first = SubtitleSegment(
            start=segment.start,
            end=request.timestamp,
            text=first_text,
        )
        second = SubtitleSegment(
            start=request.timestamp,
            end=segment.end,
            text=second_text,
        )

        index = updated.segments.index(segment)
        updated.segments[index:index + 1] = [first, second]
        return updated

    def merge_segments(
        self,
        document: SubtitleDocument,
        segment_id: UUID,
        request: MergeSegmentRequest,
    ) -> SubtitleDocument:
        updated = deepcopy(document)
        first = self.get_segment(updated, segment_id)
        second = self.get_segment(updated, request.next_segment_id)

        index = updated.segments.index(first)
        if index + 1 >= len(updated.segments):
            raise SubtitleEditorError("Next segment must follow the first segment")

        if updated.segments[index + 1].id != second.id:
            raise SubtitleEditorError("Only adjacent segments can be merged")

        merged = SubtitleSegment(
            start=min(first.start, second.start),
            end=max(first.end, second.end),
            text=f"{first.text.strip()} {second.text.strip()}".strip(),
        )
        updated.segments[index:index + 2] = [merged]
        return updated

    def update_style(
        self,
        document: SubtitleDocument,
        style: SubtitleStyle,
    ) -> SubtitleDocument:
        updated = deepcopy(document)
        updated.style = style
        return updated
