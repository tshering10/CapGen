from subtitle_editor.models import SubtitleDocument, SubtitleSegment
from video_renderer.formats import (
    generate_ass,
    generate_srt,
    seconds_to_ass,
    seconds_to_srt,
)


def test_timestamp_formatting():
    assert seconds_to_ass(3661.25) == "1:01:01.25"
    assert seconds_to_srt(3661.25) == "01:01:01,250"


def test_generate_ass_contains_subtitles_and_style():
    document = SubtitleDocument(
        segments=[
            SubtitleSegment(start=0, end=2.5, text="Hello"),
            SubtitleSegment(start=2.5, end=5, text="everyone"),
        ]
    )

    ass = generate_ass(document)

    assert "[V4+ Styles]" in ass
    assert "Style: Default" in ass
    assert "Dialogue:" in ass
    assert "Hello" in ass
    assert "everyone" in ass


def test_generate_srt():
    document = SubtitleDocument(
        segments=[SubtitleSegment(start=1, end=2.5, text="Test subtitle")]
    )

    srt = generate_srt(document)

    assert "1\n" in srt
    assert "00:00:01,000 --> 00:00:02,500" in srt
    assert "Test subtitle" in srt
