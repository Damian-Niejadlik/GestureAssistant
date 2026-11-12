from src.gesture_assistant.domain.enums import QualityStatus, TrackingStatus
from src.gesture_assistant.domain.models import PoseFrame

CORE_LANDMARK_INDICES = (0, 11, 12, 23, 24)
LOW_VISIBILITY_THRESHOLD = 0.5
OUT_OF_FRAME_MARGIN = 0.15


def evaluate_quality(frame: PoseFrame) -> tuple[QualityStatus, str | None]:
    """Ocenia widoczną jakość detekcji na podstawie punktów sylwetki."""

    if frame.landmarks is None or frame.tracking_status == TrackingStatus.NO_PERSON:
        return QualityStatus.NO_PERSON, "Nie wykryto osoby w kadrze."

    landmarks = frame.landmarks
    core_landmarks = [landmarks[index] for index in CORE_LANDMARK_INDICES if index < len(landmarks)]

    if core_landmarks:
        average_visibility = sum(landmark.visibility for landmark in core_landmarks) / len(
            core_landmarks
        )
        if average_visibility < LOW_VISIBILITY_THRESHOLD:
            return QualityStatus.LOW_VISIBILITY, "Słaba widoczność kluczowych punktów sylwetki."

    x_values = [landmark.x for landmark in landmarks]
    y_values = [landmark.y for landmark in landmarks]

    if min(x_values) < -OUT_OF_FRAME_MARGIN or max(x_values) > 1 + OUT_OF_FRAME_MARGIN:
        return QualityStatus.OUT_OF_FRAME, "Osoba jest częściowo poza kadrze."

    if min(y_values) < -OUT_OF_FRAME_MARGIN or max(y_values) > 1 + OUT_OF_FRAME_MARGIN:
        return QualityStatus.OUT_OF_FRAME, "Osoba jest częściowo poza kadrze."

    return QualityStatus.VALID, None
