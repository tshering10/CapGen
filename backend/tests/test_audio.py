import tempfile
from pathlib import Path

from transcription.audio import (
    audio_temporary_directories,
    cleanup_extracted_audio,
)


def test_cleanup_extracted_audio():
    directory = tempfile.TemporaryDirectory(prefix="capgen_test_")
    audio_path = Path(directory.name) / "audio.wav"
    audio_path.touch()
    audio_temporary_directories[str(audio_path)] = directory

    cleanup_extracted_audio(audio_path)

    assert str(audio_path) not in audio_temporary_directories
