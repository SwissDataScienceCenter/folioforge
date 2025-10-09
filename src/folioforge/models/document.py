from dataclasses import dataclass
from pathlib import Path

from folioforge.models.labels import Label


@dataclass
class BoundingBox:
    x0: float
    y0: float
    x1: float
    y1: float


@dataclass
class Area:
    """An area is a detected region in a document."""

    bbox: BoundingBox
    label: Label
    confidence: float
    converted: str | None


@dataclass
class DocumentEntry:
    """Represents a single entry in a document (e.g. page)"""

    path: Path
    layout: list[Area]
    converted: str | None


@dataclass
class DocumentReference:
    """Represents a full document getting converted."""

    path: Path
    items: list[DocumentEntry]
    converted: str | None
