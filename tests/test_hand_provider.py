import numpy as np
import pytest

from src.gesture_assistant.vision.hand_provider import (
    Hand,
    HandPoint,
    HandResult,
    MediaPipeHandProvider,
    validate_input,
)


def test_missing_hand_model(tmp_path):
    with pytest.raises(FileNotFoundError, match="modelu dłoni"):
        MediaPipeHandProvider(tmp_path / "missing.task")


def test_hand_contract_does_not_require_body():
    points = tuple(HandPoint(0.5, 0.5, 0.0) for _ in range(21))
    hand = Hand(points, points, "Left", 0.9)
    result = HandResult(1, 123, (hand,))
    assert len(result.hands[0].landmarks) == 21
    assert result.timestamp_ms == 123


@pytest.mark.parametrize(
    "frame",
    [
        np.zeros((0, 2, 3), dtype=np.uint8),
        np.zeros((2, 2), dtype=np.uint8),
        np.zeros((2, 2, 4), dtype=np.uint8),
        np.zeros((2, 2, 3), dtype=np.float32),
    ],
)
def test_reject_invalid_images(frame):
    with pytest.raises(ValueError):
        validate_input(frame, 1)


def test_valid_input():
    validate_input(np.zeros((24, 32, 3), dtype=np.uint8), 100)


def test_invalid_timestamp():
    with pytest.raises(ValueError):
        validate_input(np.zeros((24, 32, 3), dtype=np.uint8), -1)
