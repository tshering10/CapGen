from pydantic import BaseModel


class SubtitleSegment(BaseModel):
    start: float
    end: float
    text: str


class TranscriptionResult(BaseModel):
    language: str
    language_probability: float
    segments: list[SubtitleSegment]
