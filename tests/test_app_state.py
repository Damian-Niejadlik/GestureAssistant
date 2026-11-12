from src.gesture_assistant.app.app_state import AppState
from src.gesture_assistant.domain.enums import SessionState


def test_initial_state_is_idle() -> None:
    state = AppState()

    assert state.state == SessionState.IDLE
    assert state.status_message == "Gotowy"
    assert state.error_message == ""


def test_state_change_emits_signal() -> None:
    state = AppState()
    changes = []
    state.state_changed.connect(changes.append)

    state.set_state(SessionState.RUNNING)
    state.set_state(SessionState.RUNNING)

    assert changes == [SessionState.RUNNING]
    assert state.state == SessionState.RUNNING


def test_status_and_error_signals() -> None:
    state = AppState()
    statuses = []
    errors = []

    state.status_message_changed.connect(statuses.append)
    state.error_occurred.connect(errors.append)

    state.set_status_message("Śledzenie")
    state.set_error_message("Błąd kamery")

    assert statuses == ["Śledzenie"]
    assert errors == ["Błąd kamery"]
    assert state.status_message == "Śledzenie"
    assert state.error_message == "Błąd kamery"
