from dataclasses import dataclass

from src.gesture_assistant.domain.enums import QualityStatus, TrackingStatus


@dataclass(frozen=True)
class Landmark:
    x: float
    y: float
    z: float
    visibility: float
    presence: float | None = None


@dataclass(frozen=True)
class PoseFrame:
    frame_id: int
    timestamp_ms: int
    image_width: int
    image_height: int
    landmarks: list[Landmark] | None
    world_landmarks: list[Landmark] | None
    tracking_status: TrackingStatus


@dataclass(frozen=True)
class PoseResult:
    frame: PoseFrame
    quality: QualityStatus
    message: str | None = None
