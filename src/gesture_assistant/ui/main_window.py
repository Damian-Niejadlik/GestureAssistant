from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.gesture_assistant.ui.camera_view import CameraView
from src.gesture_assistant.ui.theme import get_stylesheet
from src.gesture_assistant.vision.camera_worker import CameraWorker
from src.gesture_assistant.vision.hand_provider import MediaPipeHandProvider


def default_model_path() -> Path:
    return Path(__file__).resolve().parents[3] / "models" / "hand_landmarker.task"


class MainWindow(QMainWindow):
    """Kamera i dłonie; brak wymagania widoczności całej osoby."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("GestureAssistant")
        self.setStyleSheet(get_stylesheet())
        self.resize(1024, 680)
        self._worker = None
        self._closing = False
        self._failed = False
        self._camera_index = QSpinBox()
        self._camera_index.setRange(0, 32)
        self._start_button = QPushButton("Start")
        self._stop_button = QPushButton("Stop")
        self._stop_button.setEnabled(False)
        self._camera_view = CameraView()
        self._status_label = QLabel("Gotowy — wystarczy widoczna dłoń.")
        self._error_label = QLabel()
        self._error_label.setWordWrap(True)
        self._error_label.setStyleSheet("color: #ff6b6b;")

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Numer kamery:"))
        controls.addWidget(self._camera_index)
        controls.addStretch()
        controls.addWidget(self._start_button)
        controls.addWidget(self._stop_button)
        layout = QVBoxLayout()
        layout.addLayout(controls)
        layout.addWidget(self._camera_view, 1)
        layout.addWidget(self._status_label)
        layout.addWidget(self._error_label)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self._start_button.clicked.connect(self._start_analysis)
        self._stop_button.clicked.connect(self._stop_analysis)
        self._timer = QTimer(self)
        self._timer.setInterval(33)
        self._timer.timeout.connect(self._refresh_preview)

    def _start_analysis(self) -> None:
        if self._worker is not None:
            return
        try:
            provider = MediaPipeHandProvider(default_model_path())
        except (OSError, ValueError) as exc:
            self._error_label.setText(str(exc))
            self._status_label.setText("Nie można uruchomić detekcji dłoni.")
            return
        self._failed = False
        self._error_label.clear()
        self._camera_view.clear()
        worker = CameraWorker(self._camera_index.value(), provider, parent=self)
        worker.error.connect(self._on_error)
        worker.finished.connect(self._on_worker_finished)
        self._worker = worker
        self._camera_index.setEnabled(False)
        self._start_button.setEnabled(False)
        self._stop_button.setEnabled(True)
        self._status_label.setText("Uruchamianie kamery i modelu dłoni…")
        self._timer.start()
        worker.start()

    def _stop_analysis(self) -> None:
        if self._worker is not None:
            self._stop_button.setEnabled(False)
            self._status_label.setText("Zatrzymywanie…")
            self._worker.stop()

    def _refresh_preview(self) -> None:
        if self._worker is None:
            return
        packet = self._worker.take_latest_preview()
        if packet is None:
            return
        frame, result = packet
        self._camera_view.set_frame(frame, result.hands)
        if self._failed:
            return
        if not result.hands:
            self._status_label.setText("Brak dłoni — pokaż dłoń do kamery.")
        elif any(
            p.x < 0 or p.x > 1 or p.y < 0 or p.y > 1
            for hand in result.hands
            for p in hand.landmarks
        ):
            self._status_label.setText("Dłoń częściowo poza kadrem.")
        else:
            self._status_label.setText(f"Śledzenie dłoni: {len(result.hands)}")

    def _on_error(self, message: str) -> None:
        self._failed = True
        self._status_label.setText("Błąd kamery lub detekcji dłoni.")
        self._error_label.setText(message)
        if self._worker is not None:
            self._worker.stop()

    def _on_worker_finished(self) -> None:
        self._timer.stop()
        worker = self._worker
        self._worker = None
        if worker is not None:
            worker.deleteLater()
        self._start_button.setEnabled(True)
        self._stop_button.setEnabled(False)
        self._camera_index.setEnabled(True)
        self._camera_view.clear()
        if not self._failed:
            self._status_label.setText("Kamera zatrzymana.")
        if self._closing:
            QTimer.singleShot(0, self.close)

    def closeEvent(self, event) -> None:
        if self._worker is not None:
            self._closing = True
            self._stop_analysis()
            event.ignore()
            return
        super().closeEvent(event)
