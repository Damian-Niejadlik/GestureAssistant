from pathlib import Path

from src.gesture_assistant.vision.pose_provider import MediaPipePoseProvider, PoseProvider


class ModelNotFoundError(FileNotFoundError):
    """Występuje, gdy plik modelu MediaPipe nie istnieje."""


class PoseEngine:
    """Fasada analizy sylwetki; korzysta z wybranego PoseProvider."""

    def __init__(self, provider: PoseProvider | None) -> None:
        self._provider = provider

    @classmethod
    def create(cls, model_path: Path) -> "PoseEngine":
        if not model_path.is_file():
            return cls(provider=None)

        return cls(provider=MediaPipePoseProvider(str(model_path)))

    @property
    def has_model(self) -> bool:
        return self._provider is not None

    def process(self, frame_bgr, timestamp_ms: int):
        if self._provider is None:
            raise ModelNotFoundError(
                "Brak modelu MediaPipe. Pobierz model zgodnie z instrukcją w README."
            )

        return self._provider.process(frame_bgr, timestamp_ms)

    def close(self) -> None:
        close = getattr(self._provider, "close", None)
        if callable(close):
            close()
