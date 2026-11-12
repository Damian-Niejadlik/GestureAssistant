import numpy as np
import pytest

from src.gesture_assistant.domain.enums import QualityStatus, TrackingStatus
from src.gesture_assistant.domain.models import Landmark, PoseFrame
from src.gesture_assistant.vision.pose_engine import ModelNotFoundError, PoseEngine
from src.gesture_assistant.vision.pose_provider import FakePoseProvider
from src.gesture_assistant.vision.quality import evaluate_quality


def test_fake_provider_returns_frame_with_timestamp() -> None:
    provider = FakePoseProvider()
    frame = np.zeros((240, 320, 3), dtype=np.uint8)

    result = provider.process(frame, 1234)

    assert result.frame.timestamp_ms == 1234
    assert result.frame.image_width == 320
    assert result.frame.image_height == 240
    assert result.frame.tracking_status == TrackingStatus.TRACKING
    assert result.quality == QualityStatus.VALID


def test_fake_provider_increases_frame_id() -> None:
    provider = FakePoseProvider()
    frame = np.zeros((240, 320, 3), dtype=np.uint8)

    first = provider.process(frame, 1)
    second = provider.process(frame, 2)

    assert second.frame.frame_id == first.frame.frame_id + 1


def test_pose_engine_without_model_raises_error(tmp_path) -> None:
    engine = PoseEngine.create(tmp_path / "missing.task")
    frame = np.zeros((240, 320, 3), dtype=np.uint8)

    assert engine.has_model is False

    with pytest.raises(ModelNotFoundError):
        engine.process(frame, 1)


def test_quality_no_person() -> None:
    frame = PoseFrame(
        frame_id=1,
        timestamp_ms=1,
        image_width=320,
        image_height=240,
        landmarks=None,
        world_landmarks=None,
        tracking_status=TrackingStatus.NO_PERSON,
    )

    quality, message = evaluate_quality(frame)

    assert quality == QualityStatus.NO_PERSON
    assert message is not None


def test_quality_low_visibility() -> None:
    landmarks = [Landmark(x=0.5, y=0.5, z=0.0, visibility=0.1) for _ in range(33)]
    frame = PoseFrame(
        frame_id=1,
        timestamp_ms=1,
        image_width=320,
        image_height=240,
        landmarks=landmarks,
        world_landmarks=None,
        tracking_status=TrackingStatus.TRACKING,
    )

    quality, _ = evaluate_quality(frame)

    assert quality == QualityStatus.LOW_VISIBILITY


def test_quality_out_of_frame() -> None:
    landmarks = [Landmark(x=-0.5, y=0.5, z=0.0, visibility=0.9) for _ in range(33)]
    frame = PoseFrame(
        frame_id=1,
        timestamp_ms=1,
        image_width=320,
        image_height=240,
        landmarks=landmarks,
        world_landmarks=None,
        tracking_status=TrackingStatus.TRACKING,
    )

    quality, _ = evaluate_quality(frame)

    assert quality == QualityStatus.OUT_OF_FRAME
