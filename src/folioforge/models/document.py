from pathlib import Path

from pydantic import BaseModel, field_serializer

from folioforge.models.labels import Label


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class Area(BaseModel):
    """An area is a detected region in a document."""

    bbox: BoundingBox
    label: Label
    confidence: float
    converted: str | None

    @field_serializer("label")
    def serialize_label(self, v) -> str:
        return v.name


class TableCell(BaseModel):
    bbox: BoundingBox | None
    row_span: int
    col_span: int
    start_row: int
    end_row: int
    start_col: int
    end_col: int
    converted: str | None


class Table(Area):
    headers: list[TableCell]
    cells: list[TableCell]


class ListItem(Area):
    pass


class Heading(Area):
    level: int  # same as html heading levels (1, 2, ...)


class Image(Area):
    path: Path | None = None


class Text(Area):
    pass


class DocumentEntry(BaseModel):
    """Represents a single entry in a document (e.g. page)"""

    path: Path
    layout: list[Area]
    converted: str | None


class DocumentReference(BaseModel):
    """Represents a full document getting converted."""

    path: Path
    items: list[DocumentEntry]
    converted: str | None
