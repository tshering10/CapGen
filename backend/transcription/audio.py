import shutil
import subprocess
import tempfile
from pathlib import Path


class AudioExtractionError(RuntimeError):
    pass


def extract_audio(input_path: Path) -> Path:
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        raise AudioExtractionError(
            "FFmpeg is not installed or is not available on PATH."
        )

    temporary_directory = tempfile.TemporaryDirectory(prefix="capgen_audio_")
    audio_path = Path(temporary_directory.name) / "audio.wav"

    command = [
        ffmpeg_path,
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-f",
        "wav",
        str(audio_path),
    ]

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        temporary_directory.cleanup()
        detail = exc.stderr.strip() or "FFmpeg could not process the video."
        raise AudioExtractionError(detail) from exc

    audio_path._capgen_temp_directory = temporary_directory
    return audio_path
