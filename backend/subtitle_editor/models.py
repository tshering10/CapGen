from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


class Alignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class SubtitleSegment(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    start: float = Field(ge=0)
    end: float
    text: str

    @model_validator(mode="after")
    def validate_timestamps(self) -> "SubtitleSegment":
        if self.end < self.start:
            raise ValueError("end must be greater than or equal to start")
        return self


class SubtitleStyle(BaseModel):
    preset: str = "classic"
    font_family: str = "Arial"
    font_size: int = Field(default=32, ge=8, le=160)
    font_color: str = "#FFFFFF"
    background_color: str = "#000000"
    background_opacity: float = Field(default=0.75, ge=0, le=1)
    alignment: Alignment = Alignment.CENTER
    position_x: float = Field(default=0.5, ge=0, le=1)
    position_y: float = Field(default=0.85, ge=0, le=1)


class SubtitleDocument(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    segments: list[SubtitleSegment] = Field(default_factory=list)
    style: SubtitleStyle = Field(default_factory=SubtitleStyle)


class SegmentTextUpdate(BaseModel):
    text: str


class TimestampUpdate(BaseModel):
    start: float = Field(ge=0)
    end: float

    @model_validator(mode="after")
    def validate_timestamps(self) -> "TimestampUpdate":
        if self.end < self.start:
            raise ValueError("end must be greater than or equal to start")
        return self


class SplitSegmentRequest(BaseModel):
    timestamp: float = Field(ge=0)


class MergeSegmentRequest(BaseModel):
    next_segment_id: UUID
