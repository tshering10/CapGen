import shutil
import subprocess
from pathlib import Path


class VideoRenderError(RuntimeError):
    pass


def render_video(input_path: Path, output_path: Path, ass_path: Path) -> Path:
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        raise VideoRenderError(
            "FFmpeg is not installed or is not available on PATH."
        )

    ass_filter = str(ass_path).replace("\\", "/").replace(":", "\\:")
    command = [
        ffmpeg_path,
        "-y",
        "-i",
        str(input_path),
        "-vf",
        f"ass='{ass_filter}'",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-preset",
        "veryfast",
        "-movflags",
        "+faststart",
        str(output_path),
    ]

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or "FFmpeg could not render the video."
        raise VideoRenderError(detail) from exc

    return output_path
