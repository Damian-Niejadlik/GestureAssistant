import time


def monotonic_ms() -> int:
    """Zwraca monotoniczny znacznik czasu w milisekundach."""

    return time.perf_counter_ns() // 1_000_000


def format_duration_ms(duration_ms: int) -> str:
    seconds = duration_ms // 1000
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
