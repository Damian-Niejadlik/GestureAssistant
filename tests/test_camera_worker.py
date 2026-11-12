import time

import numpy as np
import pytest

from src.gesture_assistant.vision.camera_worker import CameraWorker
from src.gesture_assistant.vision.pose_provider import FakePoseProvider


class FakeCapture:
    def __init__(self, frames, opened=True, read_delay: float = 0.0) -> None:
        self._frames = list(frames)
        self._opened = opened
        self._index = 0
        self._read_delay = read_delay
        self.released = False

    def isOpened(self) -> bool:
        return self._opened

    def read(self):
        if self._index >= len(self._frames):
            return False, None

        if self._read_delay > 0:
            time.sleep(self._read_delay)

        frame = self._frames[self._index]
        self._index += 1
        return True, frame

    def release(self) -> None:
        self.released = True


class SlowFakePoseProvider(FakePoseProvider):
    def __init__(self, processing_delay: float) -> None:
        super().__init__()
        self._processing_delay = processing_delay

    def process(self, frame_bgr, timestamp_ms: int):
        time.sleep(self._processing_delay)
        return super().process(frame_bgr, timestamp_ms)


def make_frame(value: int) -> np.ndarray:
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    frame[:, :, 0] = value
    return frame


def test_worker_processes_frames_and_releases_capture(qapp, wait_for_signal) -> None:
    frames = [make_frame(value) for value in range(3)]
    capture = FakeCapture(frames, read_delay=0.02)
    provider = FakePoseProvider()
    worker = CameraWorker(
        source=0,
        provider=provider,
        capture_factory=lambda source: capture,
    )

    received_frames = []
    received_results = []
    errors = []

    worker.frame_ready.connect(lambda frame, timestamp: received_frames.append((frame, timestamp)))
    worker.result_ready.connect(received_results.append)
    worker.error.connect(errors.append)

    worker.start()
    wait_for_signal(worker.stopped)
    assert worker.wait(5000), "Worker nie zakończył pracy w ciągu 5 sekund."
    qapp.processEvents()

    assert len(received_frames) == 3
    assert len(received_results) == 3
    assert errors, "Oczekiwano błędu po końcu źródła klatek."
    assert capture.released is True

    timestamps = [timestamp for _, timestamp in received_frames]
    assert timestamps == sorted(timestamps)
    assert len(set(timestamps)) == len(timestamps)

    processed_values = [int(frame[0, 0, 0]) for frame, _ in received_frames]
    assert processed_values == [0, 1, 2]


def test_worker_reports_camera_open_error(qapp, wait_for_signal) -> None:
    capture = FakeCapture([], opened=False)
    worker = CameraWorker(
        source=0,
        provider=FakePoseProvider(),
        capture_factory=lambda source: capture,
    )

    errors = []
    worker.error.connect(errors.append)

    worker.start()
    wait_for_signal(worker.stopped)
    assert worker.wait(5000), "Worker nie zakończył pracy w ciągu 5 sekund."
    qapp.processEvents()

    assert len(errors) == 1
    assert "Nie można otworzyć kamery" in errors[0]
    assert capture.released is True


@pytest.mark.parametrize("source", ["nieistniejacy_plik.mp4", "0", -1, True])
def test_worker_rejects_non_camera_sources(source) -> None:
    with pytest.raises(ValueError, match="numer kamery"):
        CameraWorker(source=source, provider=FakePoseProvider())


def test_worker_drops_old_frames_when_analysis_is_slow(qapp, wait_for_signal) -> None:
    frames = [make_frame(value) for value in range(20)]
    capture = FakeCapture(frames)
    provider = SlowFakePoseProvider(processing_delay=0.03)
    worker = CameraWorker(
        source=0,
        provider=provider,
        capture_factory=lambda source: capture,
    )

    received_frames = []
    worker.frame_ready.connect(lambda frame, timestamp: received_frames.append((frame, timestamp)))

    worker.start()
    wait_for_signal(worker.stopped)
    assert worker.wait(5000), "Worker nie zakończył pracy w ciągu 5 sekund."
    qapp.processEvents()

    assert 1 <= len(received_frames) < 20
    assert capture.released is True


def test_worker_stop_releases_capture(qapp, wait_for_signal) -> None:
    frames = [make_frame(value) for value in range(100)]
    capture = FakeCapture(frames, read_delay=0.01)
    worker = CameraWorker(
        source=0,
        provider=FakePoseProvider(),
        capture_factory=lambda source: capture,
    )

    worker.start()
    wait_for_signal(worker.frame_ready)
    worker.stop()
    assert worker.wait(5000), "Worker nie zakończył pracy w ciągu 5 sekund."
    qapp.processEvents()

    assert capture.released is True
    assert not worker.isRunning()
