import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task"
)
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "models" / "hand_landmarker.task"
CHUNK_SIZE = 1024 * 1024


def download_model(url: str, output: Path, timeout: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output.with_suffix(output.suffix + ".part")

    try:
        with (
            urllib.request.urlopen(url, timeout=timeout) as response,
            temporary_path.open("wb") as target,
        ):
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                target.write(chunk)
        temporary_path.replace(output)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        if temporary_path.exists():
            temporary_path.unlink()
        print(f"Nie udało się pobrać modelu: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"Model zapisano w: {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Pobiera model MediaPipe Hand Landmarker.")
    parser.add_argument("--url", default=DEFAULT_URL, help="Adres URL modelu.")
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT, help="Ścieżka docelowa modelu."
    )
    parser.add_argument("--timeout", type=int, default=60, help="Timeout połączenia w sekundach.")
    arguments = parser.parse_args()

    download_model(arguments.url, arguments.output, arguments.timeout)


if __name__ == "__main__":
    main()
