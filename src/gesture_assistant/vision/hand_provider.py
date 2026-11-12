"""Detekcja dłoni bez wymagania widoczności sylwetki."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class HandPoint:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Hand:
    landmarks: tuple[HandPoint, ...]
    world_landmarks: tuple[HandPoint, ...]
    handedness: str | None
    handedness_score: float | None


@dataclass(frozen=True)
class HandResult:
    frame_id: int
    timestamp_ms: int
    hands: tuple[Hand, ...]


def validate_input(frame: np.ndarray, timestamp_ms: int) -> None:
    if (
        not isinstance(frame, np.ndarray)
        or frame.dtype != np.uint8
        or frame.ndim != 3
        or frame.shape[2] != 3
        or frame.shape[0] == 0
        or frame.shape[1] == 0
    ):
        raise ValueError("Oczekiwano niepustego obrazu BGR uint8 z trzema kanałami.")
    if type(timestamp_ms) is not int or timestamp_ms < 0:
        raise ValueError("Timestamp musi być nieujemną liczbą całkowitą.")


class HandProvider(Protocol):
    def process(self, frame_bgr: np.ndarray, timestamp_ms: int) -> HandResult:
        """Zwraca wykryte dłonie."""


class MediaPipeHandProvider:
    """Model tworzony leniwie w wątku analizy, nie w GUI."""

    def __init__(self, model_path: Path) -> None:
        self._path = Path(model_path)
        if not self._path.is_file():
            raise FileNotFoundError(
                "Brak modelu dłoni MediaPipe.\nUruchom: python scripts/download_model.py"
            )
        self._landmarker = None
        self._last_timestamp = -1
        self._frame_id = 0
        self._closed = False

    def process(self, frame_bgr: np.ndarray, timestamp_ms: int) -> HandResult:
        validate_input(frame_bgr, timestamp_ms)
        if self._closed:
            raise RuntimeError("Provider został zamknięty.")
        if timestamp_ms <= self._last_timestamp:
            raise ValueError("Timestampy muszą być ściśle rosnące.")

        import cv2
        import mediapipe as mp
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision

        if self._landmarker is None:
            options = vision.HandLandmarkerOptions(
                base_options=python.BaseOptions(model_asset_path=str(self._path)),
                running_mode=vision.RunningMode.VIDEO,
                num_hands=2,
            )
            self._landmarker = vision.HandLandmarker.create_from_options(options)

        rgb = np.ascontiguousarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        detection = self._landmarker.detect_for_video(image, timestamp_ms)
        hands = []
        for index, points in enumerate(detection.hand_landmarks):
            categories = detection.handedness[index]
            category = categories[0] if categories else None
            world = detection.hand_world_landmarks[index]
            hands.append(
                Hand(
                    landmarks=tuple(HandPoint(p.x, p.y, p.z) for p in points),
                    world_landmarks=tuple(HandPoint(p.x, p.y, p.z) for p in world),
                    handedness=category.category_name if category else None,
                    handedness_score=category.score if category else None,
                )
            )
        self._last_timestamp = timestamp_ms
        self._frame_id += 1
        return HandResult(self._frame_id, timestamp_ms, tuple(hands))

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            if self._landmarker is not None:
                self._landmarker.close()
                self._landmarker = None
