from pathlib import Path
from threading import Lock

from faster_whisper import WhisperModel

from .models import SubtitleSegment, TranscriptionResult


class TranscriptionError(RuntimeError):
    pass


class TranscriptionService:
    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model: WhisperModel | None = None
        self._model_lock = Lock()

    def _get_model(self) -> WhisperModel:
        if self._model is None:
            with self._model_lock:
                if self._model is None:
                    self._model = WhisperModel(
                        self.model_size,
                        device=self.device,
                        compute_type=self.compute_type,
                    )
        return self._model

    def transcribe(
        self,
        audio_path: Path,
        language: str | None = None,
    ) -> TranscriptionResult:
        try:
            model = self._get_model()
            segments, transcription_info = model.transcribe(
                str(audio_path),
                language=language,
                vad_filter=True,
            )

            subtitle_segments = [
                SubtitleSegment(
                    start=float(segment.start),
                    end=float(segment.end),
                    text=segment.text.strip(),
                )
                for segment in segments
                if segment.text.strip()
            ]

            return TranscriptionResult(
                language=transcription_info.language,
                language_probability=float(
                    transcription_info.language_probability
                ),
                segments=subtitle_segments,
            )
        except Exception as exc:
            raise TranscriptionError(
                f"Speech recognition failed: {exc}"
            ) from exc
