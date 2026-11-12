# GestureAssistant

Lokalny podgląd kamery i śledzenie do dwóch dłoni. Nie trzeba pokazywać całej osoby.
Model Hand Landmarker wykrywa 21 punktów każdej dłoni, w tym nadgarstek i palce.
Nie wykrywa barku ani łokcia; pełna analiza ramienia nie jest w tej aktualizacji gotowa.
Nie ma rozpoznawania gestów, sterowania systemem ani oceny medycznej.

## Środowisko

Użytkownik potwierdził wcześniejsze testy na Windows, Python 3.12.4.
Aktualizację przygotowano na Linux, Python 3.12.8; brak fizycznej kamery i Windows.
Nie przypinamy niezweryfikowanych wersji pakietów.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts/download_model.py
.venv\Scripts\python.exe main.py
```

W już aktywnym środowisku wystarczy `python scripts/download_model.py`, potem `python main.py`.
Wybierz numer kamery i Start. Stop zwalnia kamerę i model. Brak odczytu plików wideo.
Model jest lokalny: `models/hand_landmarker.task`.
Stary model `pose_landmarker_lite.task` nie jest zamiennikiem modelu dłoni.
Skrypt pobierania jest opcjonalny, ma timeout; GUI nie pobiera nic automatycznie.

## Weryfikacja

```powershell
python -m pytest -v
python -m ruff format .
python -m ruff check .
```

## Ograniczenia

Śledzenie może zanikać przy zasłonięciu palców i słabym świetle.
Brak detekcji nie pozwala rozstrzygnąć, czy dłoń jest zasłonięta, poza kadrem czy nieobecna.
Nie fabrykujemy visibility/presence dla dłoni; wynik handedness to pewność klasyfikacji
lewa/prawa, a nie widoczność punktów.
VIDEO w API MediaPipe oznacza tutaj synchroniczną analizę kolejnych klatek kamery,
nie możliwość otwarcia pliku w aplikacji.
Zablokowany natywny odczyt sterownika kamery może opóźnić Stop. Nie zabijamy wątku siłowo.
Starsze moduły Pose i ich testy pozostają jako nieaktywna warstwa zgodności.
Importy mają postać `from src.gesture_assistant...`; uruchamiaj polecenia z katalogu projektu.
