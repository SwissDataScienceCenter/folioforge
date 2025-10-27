from pathlib import Path

import cv2
from bs4 import BeautifulSoup
from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.renderers.chunk import FlatBlockOutput

from folioforge.extraction.protocol import Extractor
from folioforge.models.document import Area, BoundingBox, DocumentEntry, Heading, Image, ListItem, Table, TableCell, Text
from folioforge.models.labels import Label


class MarkerPDFExtractor(Extractor):
    supports_pickle = True

    def __init__(self, min_confidence: float = 0.2) -> None:
        self.min_confidence = min_confidence
        self.config = {"output_format": "chunks", "detection_line_min_confidence": self.min_confidence}
        self.parsed_config = ConfigParser(self.config)
        self.converter = PdfConverter(
            config=self.parsed_config.generate_config_dict(),
            artifact_dict=create_model_dict(),
            processor_list=self.parsed_config.get_processors(),
            renderer=self.parsed_config.get_renderer(),
            llm_service=self.parsed_config.get_llm_service(),
        )

    def extract(self, entry: DocumentEntry) -> DocumentEntry:
        result = self.converter(str(entry.path))
        entry.layout = []
        for chunk in result.blocks:
            if not chunk.html:
                continue
            entry.layout.extend(self._chunk_to_areas(chunk, entry))

        return entry

    def _chunk_to_areas(self, chunk: FlatBlockOutput, entry: DocumentEntry) -> list[Area]:
        match chunk.block_type:
            case "SectionHeader":
                return [self._convert_header(chunk)]

            case "Table" | "TableOfContents":
                return [self._convert_table(chunk)]

            case "Picture" | "PictureGroup" | "Figure" | "FigureGroup":
                return [self._convert_image(chunk, entry)]

            case "ListGroup":
                return self._convert_list(chunk)

            case _:
                return [self._convert_text(chunk)]

    def _convert_header(self, chunk: FlatBlockOutput) -> Area:
        soup = BeautifulSoup(chunk.html, "html.parser")
        content = "\n".join(soup.contents[0].stripped_strings)
        level = 1
        match soup.contents[0].name:  # type: ignore
            case "h1":
                level = 1
            case "h2":
                level = 2
            case "h3":
                level = 3
            case "h4":
                level = 4
            case "h5":
                level = 5
            case "h6":
                level = 6
        return Heading(
            bbox=BoundingBox(x0=chunk.bbox[0], y0=chunk.bbox[1], x1=chunk.bbox[2], y1=chunk.bbox[3]),
            label=Label.SECTION_HEADER,
            confidence=1.0,  # marker does not output confidence
            converted=content,
            level=level,
        )

    def _convert_table(self, chunk: FlatBlockOutput) -> Area:
        soup = BeautifulSoup(chunk.html, "html.parser")
        headers = []
        cells = []
        for i, row in enumerate(soup.find_all("tr")):
            for j, element in enumerate(row.find_all(["th", "td"])):
                rowspan = int(element.attrs.get("rowspan", 1))
                colspan = int(element.attrs.get("colspan", 1))
                cell = TableCell(
                    bbox=None,
                    row_span=rowspan,
                    col_span=colspan,
                    start_row=i,
                    start_col=j,
                    end_row=i + rowspan,
                    end_col=j + colspan,
                    converted=element.get_text(),
                )
                if element.name == "th":
                    headers.append(cell)
                else:
                    cells.append(cell)

        return Table(
            bbox=BoundingBox(x0=chunk.bbox[0], y0=chunk.bbox[1], x1=chunk.bbox[2], y1=chunk.bbox[3]),
            label=Label.TABLE,
            headers=headers,
            cells=cells,
            confidence=1.0,  # marker does not output confidence
            converted=chunk.html,
        )

    def _convert_image(self, chunk: FlatBlockOutput, entry: DocumentEntry) -> Area:
        img = cv2.imread(str(entry.path))
        assert img is not None
        img_path = Path(entry.path).parent / f"image_{entry.path.stem}_{chunk.id.replace('/', '_')}.png"
        cropped = img[int(chunk.bbox[1]) : int(chunk.bbox[3]), int(chunk.bbox[0]) : int(chunk.bbox[2])]
        cv2.imwrite(str(img_path), cropped)
        return Image(
            bbox=BoundingBox(x0=chunk.bbox[0], y0=chunk.bbox[1], x1=chunk.bbox[2], y1=chunk.bbox[3]),
            label=Label.IMAGE,
            path=img_path,
            confidence=1.0,  # marker does not output confidence
            converted=None,
        )

    def _convert_list(self, chunk: FlatBlockOutput) -> list[Area]:
        soup = BeautifulSoup(chunk.html, "html.parser")
        bbox = BoundingBox(x0=chunk.bbox[0], y0=chunk.bbox[1], x1=chunk.bbox[2], y1=chunk.bbox[3])
        # Note: marker does not provide bounding boxes for individual list items, we just linearily interpolate them
        items = soup.find_all("li")
        return [
            ListItem(
                bbox=BoundingBox(
                    x0=bbox.x0,
                    y0=bbox.y0 + i * (bbox.y1 - bbox.y0) / len(items),
                    x1=bbox.x1,
                    y1=bbox.y0 + (i + 1) * (bbox.y1 - bbox.y0) / len(items),
                ),
                label=Label.LIST_ITEM,
                confidence=1.0,
                converted=item.text,
            )
            for i, item in enumerate(items)
        ]

    def _convert_text(self, chunk: FlatBlockOutput) -> Area:
        match chunk.block_type:
            case "Span" | "Line" | "Char" | "Code" | "Form" | "TextInlineMath" | "Text" | "Reference":
                label = Label.TEXT
                cls = Text

            case "Footnote":
                label = Label.FOOTNOTE
                cls = Text

            case "PagerHeader":
                label = Label.PAGE_HEADER
                cls = Text
            case "PageFooter":
                label = Label.PAGE_FOOTER
                cls = Text
            case _:
                label = Label.OTHER
                cls = Area
        soup = BeautifulSoup(chunk.html, "html.parser")
        content = "\n".join(soup.contents[0].stripped_strings)
        return cls(
            bbox=BoundingBox(x0=chunk.bbox[0], y0=chunk.bbox[1], x1=chunk.bbox[2], y1=chunk.bbox[3]),
            label=label,
            confidence=1.0,  # marker does not output confidence
            converted=content,
        )
