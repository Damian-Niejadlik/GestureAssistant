# Architektura GestureAssistant — aktualizacja dłoni

Kamera (numer całkowity >= 0) -> wątek odczytu -> bufor wejściowy 1 klatki
-> CameraWorker/QThread -> MediaPipeHandProvider -> HandResult
-> bufor wyjściowy 1 pary (obraz, wynik) -> QTimer GUI -> CameraView.

Brak wejścia plikowego. Konstruktor workera odrzuca str, bool i ujemne numery.
GUI nie podłącza sygnałów przenoszących każdy obraz: pobiera najnowszy pakiet co 33 ms.
Sygnały frame_ready/result_ready pozostają do testów i integracji; podłączenie ich
przez zewnętrzny kod do powolnego odbiorcy wymaga własnego backpressure.
Obraz i szkielet w GUI pochodzą z tej samej klatki.

HandPoint: x/y znormalizowane względem obrazu, z względna głębokość.
Hand: 21 punktów lokalnych, 21 world_landmarks, handedness i jej score.
World landmarks są w metrach, nie w znormalizowanych współrzędnych obrazu.
HandResult: frame_id, timestamp_ms, tuple dłoni; brak dłoni to pusta tuple.
Nie używamy wskaźników widoczności sylwetki do odrzucania dłoni.

Model powstaje leniwie w process(), w wątku analizy. Worker zamyka provider po analizie.
Kamera jest otwierana, odczytywana i zwalniana w jednym wątku odczytu.
Stop zleca zatrzymanie; zamknięcie okna czeka asynchronicznie na QThread.finished.
Nie ma terminate(). Bufory wejścia i podglądu są ograniczone.
Stare PoseFrame/PoseProvider/quality są zachowane, ale nieużywane w nowej ścieżce GUI.
Wszystkie importy projektu używają src.gesture_assistant.
