from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import TypeVar

T = TypeVar("T", bound=IntEnum)


@dataclass
class Area[T]:
    bbox: tuple[float, float, float, float]
    label: T
    confidence: float
    converted: str | None


@dataclass
class Layout[T]:
    areas: list[Area[T]]


@dataclass
class DocumentReference[T]:
    path: Path
    items: list[Path]
    layout: Layout[T]
    converted: str | None
