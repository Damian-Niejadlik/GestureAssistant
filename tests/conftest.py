import pytest
from PySide6.QtCore import QCoreApplication, QEventLoop, QTimer


@pytest.fixture(scope="session")
def qapp():
    application = QCoreApplication.instance()

    if application is None:
        application = QCoreApplication([])

    yield application


@pytest.fixture
def wait_for_signal(qapp):
    def _wait(signal, timeout_ms: int = 5000) -> None:
        loop = QEventLoop()
        signal.connect(loop.quit)
        QTimer.singleShot(timeout_ms, loop.quit)
        loop.exec()

    return _wait
