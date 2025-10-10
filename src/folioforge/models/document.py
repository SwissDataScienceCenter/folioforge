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
class TableCell:
    bbox: BoundingBox | None
    row_span: int
    col_span: int
    start_row: int
    end_row: int
    start_col: int
    end_col: int
    converted: str | None


@dataclass
class Table(Area):
    headers: list[TableCell]
    cells: list[TableCell]


@dataclass
class ListItem(Area):
    pass


@dataclass
class Heading(Area):
    level: int  # same as html heading levels (1, 2, ...)


@dataclass
class Image(Area):
    pass


@dataclass
class Text(Area):
    pass


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
