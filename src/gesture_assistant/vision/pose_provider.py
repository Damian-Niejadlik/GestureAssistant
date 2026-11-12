from typing import Protocol

import numpy as np

from src.gesture_assistant.domain.enums import QualityStatus, TrackingStatus
from src.gesture_assistant.domain.models import Landmark, PoseFrame, PoseResult
from src.gesture_assistant.vision.quality import evaluate_quality


class PoseProvider(Protocol):
    def process(self, frame_bgr: np.ndarray, timestamp_ms: int) -> PoseResult:
        """Analizuje jedną klatkę BGR i zwraca wynik detekcji sylwetki."""


class FakePoseProvider:
    """Atrapa dostawcy wyników wyłącznie do testów i prezentacji interfejsu."""

    def __init__(
        self,
        tracking_status: TrackingStatus = TrackingStatus.TRACKING,
        quality: QualityStatus = QualityStatus.VALID,
        message: str | None = None,
        landmarks: list[Landmark] | None = None,
    ) -> None:
        self._tracking_status = tracking_status
        self._quality = quality
        self._message = message
        self._landmarks = landmarks
        self._frame_id = 0

    def process(self, frame_bgr: np.ndarray, timestamp_ms: int) -> PoseResult:
        if frame_bgr.ndim != 3:
            raise ValueError("Oczekiwano obrazu BGR o trzech wymiarach.")

        height, width = frame_bgr.shape[:2]
        self._frame_id += 1

        frame = PoseFrame(
            frame_id=self._frame_id,
            timestamp_ms=timestamp_ms,
            image_width=width,
            image_height=height,
            landmarks=self._landmarks,
            world_landmarks=None,
            tracking_status=self._tracking_status,
        )

        return PoseResult(
            frame=frame,
            quality=self._quality,
            message=self._message,
        )


class MediaPipePoseProvider:
    """Dostawca wyników oparty o MediaPipe Pose Landmarker."""

    def __init__(self, model_path: str) -> None:
        import cv2
        import mediapipe as mp
        from mediapipe.tasks import python as mediapipe_python
        from mediapipe.tasks.python import vision

        self._cv2 = cv2
        self._mp = mp
        base_options = mediapipe_python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1,
        )
        self._landmarker = vision.PoseLandmarker.create_from_options(options)
        self._frame_id = 0

    def process(self, frame_bgr: np.ndarray, timestamp_ms: int) -> PoseResult:
        rgb = self._cv2.cvtColor(frame_bgr, self._cv2.COLOR_BGR2RGB)
        image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb)
        detection = self._landmarker.detect_for_video(image, timestamp_ms)
        self._frame_id += 1

        landmarks = self._convert_landmarks(detection.pose_landmarks)
        world_landmarks = self._convert_landmarks(detection.pose_world_landmarks)
        tracking_status = TrackingStatus.TRACKING if landmarks else TrackingStatus.NO_PERSON

        frame = PoseFrame(
            frame_id=self._frame_id,
            timestamp_ms=timestamp_ms,
            image_width=frame_bgr.shape[1],
            image_height=frame_bgr.shape[0],
            landmarks=landmarks,
            world_landmarks=world_landmarks,
            tracking_status=tracking_status,
        )

        quality, message = evaluate_quality(frame)
        return PoseResult(frame=frame, quality=quality, message=message)

    def close(self) -> None:
        self._landmarker.close()

    def _convert_landmarks(self, raw_landmarks) -> list[Landmark] | None:
        if not raw_landmarks:
            return None

        return [
            Landmark(
                x=landmark.x,
                y=landmark.y,
                z=landmark.z,
                visibility=landmark.visibility,
                presence=getattr(landmark, "presence", None),
            )
            for landmark in raw_landmarks[0]
        ]
