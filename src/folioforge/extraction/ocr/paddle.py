import cv2
from numpy import ndarray
from paddleocr import PaddleOCR, TableStructureRecognition

from folioforge.extraction.ocr.protocol import OcrExtractor
from folioforge.models.document import BoundingBox, DocumentEntry, Image, Table, TableCell


class PaddleOcrExtractor(OcrExtractor):
    supports_pickle = False

    def __init__(self):
        self.ocr = PaddleOCR(use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=False)
        self.table_ocr = TableStructureRecognition(model_name="SLANet")

    def extract(self, entry: DocumentEntry) -> DocumentEntry:
        img = cv2.imread(str(entry.path))
        for area in entry.layout:
            cropped_img = img[int(area.bbox.y0) : int(area.bbox.y1), int(area.bbox.x0) : int(area.bbox.x1), :]
            if isinstance(area, Image):
                continue
            elif isinstance(area, Table):
                self.extract_table(cropped_img, img, area)
            else:
                output = self.ocr.ocr(cropped_img)
                area.converted = " ".join(output[0]["rec_texts"])
        return entry

    def extract_table(self, cropped_image: ndarray, full_image: ndarray, table: Table, padding: int = 5) -> None:
        if not table.cells:
            # layout detection only detected the whole table, so we do table detection now
            output = self.table_ocr.predict(cropped_image)[0]
            bboxes = [
                BoundingBox(
                    x0=min(b[0], b[2], b[4], b[6]) + table.bbox.x0 - padding,
                    y0=min(b[1], b[3], b[5], b[7]) + table.bbox.y0 - padding,
                    x1=max(b[0], b[2], b[4], b[6]) + table.bbox.x0 + padding,
                    y1=max(b[1], b[3], b[5], b[7]) + table.bbox.y0 + padding,
                )
                for b in output["bbox"]
            ]
            structure = output["structure"]

            row = -1
            col = -1
            current_cell = None
            cells = []

            for entry in structure:
                if entry == "<tr>":
                    row += 1
                    col = -1
                elif entry in ["<td></td>", "<td"]:
                    col += 1
                    if current_cell is not None:
                        cells.append(current_cell)
                    bbox = bboxes.pop(0)
                    current_cell = TableCell(
                        bbox=bbox, start_row=row, start_col=col, row_span=1, col_span=1, end_row=row + 1, end_col=col + 1, converted=None
                    )
                elif entry.startswith("colspan"):
                    if current_cell is not None:
                        current_cell.col_span = int(entry.split("=")[1].trim('"'))
                elif entry.startswith("rowspan"):
                    if current_cell is not None:
                        current_cell.row_span = int(entry.split("=")[1].trim('"'))
            if current_cell is not None:
                cells.append(current_cell)
            table.headers = [c for c in cells if c.start_row == 0]
            table.cells = [c for c in cells if c.start_row != 0]

        for header in table.headers:
            if not header.bbox:
                continue
            output = self.ocr.predict(full_image[int(header.bbox.y0) : int(header.bbox.y1), int(header.bbox.x0) : int(header.bbox.x1), :])
            header.converted = " ".join(output[0]["rec_texts"])
        for cell in table.cells:
            if not cell.bbox:
                continue
            output = self.ocr.predict(full_image[int(cell.bbox.y0) : int(cell.bbox.y1), int(cell.bbox.x0) : int(cell.bbox.x1), :])
            cell.converted = " ".join(output[0]["rec_texts"])
