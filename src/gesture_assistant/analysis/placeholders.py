"""Miejsce na przyszłą analizę techniki ćwiczeń.

Implementacja analizy ruchu, faz ćwiczenia i licznika powtórzeń będzie dodana
w kolejnym etapie. Ten moduł nie wykonuje jeszcze żadnej analizy.
"""

from src.gesture_assistant.domain.enums import ExerciseType

SUPPORTED_EXERCISES: tuple[ExerciseType, ...] = (
    ExerciseType.SQUAT,
    ExerciseType.PUSHUP,
    ExerciseType.PLANK,
)
