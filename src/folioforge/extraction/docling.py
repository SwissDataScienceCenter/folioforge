from typing import cast

from docling.datamodel.base_models import Table as DoclingTable
from docling.document_converter import DocumentConverter
from docling_core.types.doc.labels import DocItemLabel

from folioforge.extraction.protocol import Extractor
from folioforge.models.document import Area, BoundingBox, DocumentEntry, Heading, Image, Table, TableCell
from folioforge.models.labels import Label


class DoclingExtractor(Extractor):
    def __init__(self) -> None:
        self.converter = DocumentConverter()

    def __map_label(self, label: DocItemLabel) -> Label:
        match label:
            case DocItemLabel.CAPTION:
                return Label.CAPTION
            case DocItemLabel.LIST_ITEM:
                return Label.LIST_ITEM
            case DocItemLabel.PAGE_FOOTER:
                return Label.PAGE_FOOTER
            case DocItemLabel.PAGE_HEADER:
                return Label.PAGE_HEADER
            case DocItemLabel.PICTURE:
                return Label.IMAGE
            case DocItemLabel.SECTION_HEADER:
                return Label.SECTION_HEADER
            case DocItemLabel.FOOTNOTE:
                return Label.FOOTNOTE
            case DocItemLabel.TABLE:
                return Label.TABLE
            case DocItemLabel.TEXT:
                return Label.TEXT
            case DocItemLabel.TITLE:
                return Label.TITLE
            case _:
                return Label.OTHER

    def extract(self, entry: DocumentEntry) -> DocumentEntry:
        result = next(self.converter.convert_all(source=[entry.path]))
        for unit in result.assembled.elements:
            bbox = unit.cluster.bbox
            label = self.__map_label(unit.label)
            bbox = BoundingBox(x0=bbox.l, y0=bbox.t, x1=bbox.r, y1=bbox.b)
            area: Area
            match label:
                case Label.TABLE:
                    table = cast(DoclingTable, unit)
                    headers = []
                    cells = []
                    for c in table.table_cells:
                        cell_bbox = None
                        if c.bbox:
                            cell_bbox = BoundingBox(x0=c.bbox.l, y0=c.bbox.t, x1=c.bbox.r, y1=c.bbox.b)
                        cell = TableCell(
                            bbox=cell_bbox,
                            row_span=c.row_span,
                            col_span=c.col_span,
                            start_row=c.start_col_offset_idx,
                            end_row=c.end_row_offset_idx,
                            start_col=c.start_col_offset_idx,
                            end_col=c.end_col_offset_idx,
                            converted=c.text,
                        )
                        if c.column_header:
                            headers.append(cell)
                        else:
                            cells.append(cell)
                    area = Table(
                        bbox=bbox, label=Label.TABLE, confidence=unit.cluster.confidence, headers=headers, cells=cells, converted=None
                    )
                case Label.IMAGE:
                    area = Image(bbox=bbox, label=label, confidence=unit.cluster.confidence, converted=unit.text)
                case Label.TITLE:
                    area = Heading(level=1, bbox=bbox, label=label, confidence=unit.cluster.confidence, converted=unit.text)
                case Label.SECTION_HEADER:
                    area = Heading(level=2, bbox=bbox, label=label, confidence=unit.cluster.confidence, converted=unit.text)
                case _:
                    area = Area(
                        bbox=bbox,
                        label=label,
                        confidence=unit.cluster.confidence,
                        converted=unit.text,
                    )
            entry.layout.append(area)
        entry.converted = result.document.export_to_markdown()
        return entry
