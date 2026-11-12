from enum import Enum, auto


class TrackingStatus(Enum):
    NO_PERSON = auto()
    TRACKING = auto()
    LOST = auto()


class QualityStatus(Enum):
    VALID = auto()
    NO_PERSON = auto()
    LOW_VISIBILITY = auto()
    OUT_OF_FRAME = auto()
    MULTIPLE_PEOPLE = auto()
    WRONG_VIEW = auto()
    CAMERA_ERROR = auto()


class ExerciseType(Enum):
    SQUAT = auto()
    PUSHUP = auto()
    PLANK = auto()


class SessionState(Enum):
    IDLE = auto()
    CALIBRATING = auto()
    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()
    ERROR = auto()
