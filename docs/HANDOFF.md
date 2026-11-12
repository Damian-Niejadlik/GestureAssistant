# Handoff — aktualizacja dłoni i kamery

## Zmienione

- Osobny provider dłoni, do dwóch dłoni; bez wymogu sylwetki.
- GUI wyłącznie kamera, brak ścieżki pliku i dialogów wideo.
- Kamera wymaga nieujemnego int; test pliku zastąpiono testem odrzucania źródła.
- Zachowane poprzednie testy modeli, jakości Pose i stanu; Pose nie jest aktywną detekcją.
- Input buffer i GUI mailbox mają pojemność 1. Overlay odpowiada aktualnemu obrazowi.
- Model tworzony w workerze, zamykany w finally; GUI reaguje na finished.
- Poprawiona ścieżka modelu (rodzic projektu, nie katalog src).

## Model

Uruchom ręcznie: `python scripts/download_model.py`.
Plik: models/hand_landmarker.task.
URL: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
Brak modelu daje czytelny komunikat. Nie ma pobierania przy każdym starcie GUI.

## Nadal do wykonania

- Manualna weryfikacja Windows/kamera/MediaPipe.
- Rozpoznawanie gestów i ewentualne pomocnicze punkty łokcia/barku.
  Hand Landmarker nie zapewnia tych punktów.
- Rozwiązanie blokady natywnego read() sterownika (np. izolacja kamery w procesie).
- Stary test trzech klatek używa opóźnienia 20 ms i może być zależny od planisty;
  docelowo zastąpić synchronizowaną atrapą zamiast zwiększania opóźnień.
- Brak medycznej interpretacji wyników i brak pełnej analizy ćwiczeń.

Wyniki wykonanych sprawdzeń są zapisane w docs/VERIFICATION.md.
Nie deklarujemy pełnej sprawności bez testów użytkownika na sprzęcie.
