from PySide6.QtCore import QObject, Signal

from src.gesture_assistant.domain.enums import SessionState


class AppState(QObject):
    state_changed = Signal(object)
    status_message_changed = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._state = SessionState.IDLE
        self._status_message = "Gotowy"
        self._error_message = ""

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def status_message(self) -> str:
        return self._status_message

    @property
    def error_message(self) -> str:
        return self._error_message

    def set_state(self, state: SessionState) -> None:
        if state == self._state:
            return
        self._state = state
        self.state_changed.emit(state)

    def set_status_message(self, message: str) -> None:
        if message == self._status_message:
            return
        self._status_message = message
        self.status_message_changed.emit(message)

    def set_error_message(self, message: str) -> None:
        if message == self._error_message:
            return
        self._error_message = message
        self.error_occurred.emit(message)

    def clear_error_message(self) -> None:
        self.set_error_message("")
