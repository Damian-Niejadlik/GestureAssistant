# Rzeczywista weryfikacja aktualizacji

Środowisko: Linux, Python 3.12.8.
Utworzono lokalny venv przez python -m venv --system-site-packages work/check_venv.
Nie instalowano nic globalnie ani nie pobierano modelu.
W venv udostępniono już zainstalowane biblioteki środowiska przez system-site-packages.

1. Odtworzono 36 plików z dostarczonego GestureAssistant_kod.txt.
2. Sprawdzono składnię 32 plików Python przez ast.parse: bez błędów.
3. Uruchomiono izolowaną kopię tests/test_hand_provider.py poza katalogiem fixtures Qt:
   python -m pytest -v --confcutdir <katalog_izolowany> <test_hand_provider.py>.
   Wynik: 8 passed in 0.14s. Żadnych testów nie pominięto w tym izolowanym module.
4. Pełne python -m pytest -v: kod 4, ModuleNotFoundError: No module named 'PySide6'.
5. python -m ruff check .: kod 1, No module named ruff.

Nie uruchomiono GUI, rzeczywistego modelu MediaPipe ani kamery. Brak Windows i GPU.
8 testów nie potwierdza działania MediaPipe ani wątków Qt; sprawdza tylko kontrakty,
brak pliku modelu oraz walidację obrazów i timestampów.
Pełne testy oraz lint wymagają uruchomienia w istniejącym venv użytkownika.
