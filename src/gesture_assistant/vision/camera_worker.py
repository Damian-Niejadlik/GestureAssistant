import logging
import queue
import threading

import cv2
from PySide6.QtCore import QThread, Signal

from src.gesture_assistant.utils.time_utils import monotonic_ms
from src.gesture_assistant.vision.hand_provider import HandProvider

logger = logging.getLogger(__name__)


class CameraWorker(QThread):
    """Odczyt źródła i analiza z buforem najnowszej klatki."""

    frame_ready = Signal(object, object)
    result_ready = Signal(object)
    error = Signal(str)
    stopped = Signal()

    def __init__(
        self,
        source: int,
        provider: HandProvider,
        capture_factory=cv2.VideoCapture,
        parent=None,
    ) -> None:
        super().__init__(parent)

        if type(source) is not int or source < 0:
            raise ValueError("Źródłem musi być nieujemny numer kamery, nie plik wideo.")
        self._source = source
        self._provider = provider
        self._capture_factory = capture_factory

        self._stop_event = threading.Event()
        self._capture_finished = threading.Event()
        self._latest_frame = queue.Queue(maxsize=1)
        self._preview_lock = threading.Lock()
        self._preview = None

    def run(self) -> None:
        capture_thread = threading.Thread(
            target=self._capture_loop,
            name="GestureAssistantCapture",
            daemon=False,
        )

        try:
            capture_thread.start()

            while not self._stop_event.is_set():
                try:
                    frame, timestamp_ms = self._latest_frame.get(timeout=0.1)
                except queue.Empty:
                    if self._capture_finished.is_set():
                        # Producent już nie doda kolejnych klatek.
                        # Sprawdzamy kolejkę ponownie, aby nie pominąć
                        # ostatniej klatki dodanej tuż przed końcem odczytu.
                        try:
                            frame, timestamp_ms = self._latest_frame.get_nowait()
                        except queue.Empty:
                            break
                    else:
                        continue

                try:
                    result = self._provider.process(frame, timestamp_ms)
                except Exception as exc:
                    logger.exception("Błąd podczas analizy klatki.")
                    self.error.emit(f"Błąd analizy klatki: {exc}")
                    break

                with self._preview_lock:
                    self._preview = (frame, result)
                self.frame_ready.emit(frame, timestamp_ms)
                self.result_ready.emit(result)

        except Exception as exc:
            logger.exception("Błąd uruchomienia lub pracy workera.")
            self.error.emit(f"Błąd workera: {exc}")

        finally:
            self._stop_event.set()

            if capture_thread.ident is not None:
                # Nie zgłaszamy zakończenia, dopóki wątek odczytu
                # faktycznie nie zwolni źródła i nie zakończy pracy.
                capture_thread.join()

            try:
                close = getattr(self._provider, "close", None)
                if callable(close):
                    close()
            except Exception as exc:
                logger.exception("Błąd zamykania modelu.")
                self.error.emit(f"Błąd zamykania modelu: {exc}")
            finally:
                self.stopped.emit()

    def stop(self) -> None:
        """Zleca zatrzymanie bez blokowania głównego wątku GUI."""
        self._stop_event.set()

    def _capture_loop(self) -> None:
        capture = None
        last_timestamp_ms = -1

        try:
            capture = self._capture_factory(self._source)

            if not capture.isOpened():
                message = f"Nie można otworzyć kamery o numerze {self._source}."

                logger.error(message)
                self.error.emit(message)
                return

            while not self._stop_event.is_set():
                opened, frame = capture.read()

                if not opened:
                    if not self._stop_event.is_set():
                        self.error.emit("Nie można odczytać kolejnej klatki z kamery.")
                    break

                if self._stop_event.is_set():
                    break

                if frame is None:
                    self.error.emit("Kamera zwróciło pustą klatkę.")
                    break

                timestamp_ms = max(
                    monotonic_ms(),
                    last_timestamp_ms + 1,
                )
                last_timestamp_ms = timestamp_ms

                self._publish_latest_frame(frame, timestamp_ms)

        except Exception as exc:
            logger.exception("Błąd odczytu kamery.")
            self.error.emit(f"Błąd kamery: {exc}")

        finally:
            try:
                if capture is not None:
                    capture.release()
            except Exception as exc:
                logger.exception("Błąd zwalniania kamery.")
                self.error.emit(f"Błąd zwalniania kamery: {exc}")
            finally:
                self._capture_finished.set()

    def _publish_latest_frame(self, frame, timestamp_ms: int) -> None:
        """Zastępuje oczekującą klatkę nowszą, jeśli bufor jest pełny."""
        item = (frame, timestamp_ms)

        try:
            self._latest_frame.put_nowait(item)
            return
        except queue.Full:
            # Pełna kolejka oznacza, że można odrzucić starszą klatkę.
            logger.debug("Odrzucanie starszej klatki z bufora.")

        try:
            self._latest_frame.get_nowait()
        except queue.Empty:
            # Konsument mógł już pobrać starszą klatkę.
            logger.debug("Starsza klatka została już pobrana.")

        # Tylko ten wątek jest producentem. Po usunięciu elementu
        # lub pobraniu go przez konsumenta jest miejsce w kolejce.
        self._latest_frame.put_nowait(item)

    def take_latest_preview(self):
        """GUI odbiera najwyżej jeden aktualny pakiet, bez kolejki sygnałów obrazu."""
        with self._preview_lock:
            preview = self._preview
            self._preview = None
            return preview
