from subtitle_editor.models import SubtitleDocument, SubtitleSegment
from subtitle_editor.store import (
    create_document,
    get_document,
    update_document,
)


def test_shared_document_store_round_trip():
    document = SubtitleDocument(
        segments=[SubtitleSegment(start=0, end=1, text="Hello")]
    )
    create_document(document)

    stored = get_document(str(document.id))
    assert stored is not None
    assert stored.segments[0].text == "Hello"

    updated = stored.model_copy(
        update={"segments": [SubtitleSegment(start=0, end=1, text="Updated")]}
    )
    update_document(updated)

    assert get_document(str(document.id)).segments[0].text == "Updated"
