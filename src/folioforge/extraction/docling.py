from docling.document_converter import DocumentConverter
from docling_core.types.doc.labels import DocItemLabel

from folioforge.extraction.protocol import Extractor
from folioforge.models.document import Area, BoundingBox, DocumentEntry
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
            area = Area(
                bbox=BoundingBox(bbox.l, bbox.t, bbox.r, bbox.b),
                label=self.__map_label(unit.label),
                confidence=unit.cluster.confidence,
                converted=unit.text,
            )
            entry.layout.append(area)
        entry.converted = result.document.export_to_markdown()
        return entry
