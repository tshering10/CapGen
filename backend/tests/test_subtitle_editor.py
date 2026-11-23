from subtitle_editor.models import (
    MergeSegmentRequest,
    SplitSegmentRequest,
    SubtitleDocument,
    SubtitleSegment,
)
from subtitle_editor.service import SubtitleEditorError, SubtitleEditorService


def test_split_segment():
    service = SubtitleEditorService()
    first = SubtitleSegment(start=0, end=4, text="Hello everyone")
    document = SubtitleDocument(segments=[first])

    result = service.split_segment(
        document,
        first.id,
        SplitSegmentRequest(timestamp=2),
    )

    assert len(result.segments) == 2
    assert result.segments[0].text == "Hello"
    assert result.segments[1].text == "everyone"


def test_merge_adjacent_segments():
    service = SubtitleEditorService()
    first = SubtitleSegment(start=0, end=2, text="Hello")
    second = SubtitleSegment(start=2, end=4, text="everyone")
    document = SubtitleDocument(segments=[first, second])

    result = service.merge_segments(
        document,
        first.id,
        MergeSegmentRequest(next_segment_id=second.id),
    )

    assert len(result.segments) == 1
    assert result.segments[0].text == "Hello everyone"
    assert result.segments[0].start == 0
    assert result.segments[0].end == 4


def test_split_rejects_timestamp_outside_segment():
    service = SubtitleEditorService()
    segment = SubtitleSegment(start=1, end=3, text="Hello")
    document = SubtitleDocument(segments=[segment])

    try:
        service.split_segment(
            document,
            segment.id,
            SplitSegmentRequest(timestamp=4),
        )
        assert False, "Expected SubtitleEditorError"
    except SubtitleEditorError:
        pass
