from folioforge.extraction.ocr.protocol import OcrExtractor
from folioforge.models.document import DocumentEntry, Image, Table
from folioforge.models.labels import Label
from paddleocr import PaddleOCR, TableStructureRecognition
import cv2


class PaddleOcrExtractor(OcrExtractor):
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
                if not area.cells:
                    # layout detection only detected the whole table, so we do table detection now
                    # TODO: implement table cell detection and extraction
                    output = self.ocr.predict(img)
                    area.converted = " | ".join(output[0]["rec_texts"])
                for header in area.headers:
                    if not header.bbox:
                        continue
                    output = self.ocr.predict(img[int(header.bbox.y0) : int(header.bbox.y1), int(header.bbox.x0) : int(header.bbox.x1), :])
                    header.converted = " ".join(output[0]["rec_texts"])
                for cell in area.cells:
                    if not cell.bbox:
                        continue
                    output = self.ocr.predict(img[int(cell.bbox.y0) : int(cell.bbox.y1), int(cell.bbox.x0) : int(cell.bbox.x1), :])
                    cell.converted = " ".join(output[0]["rec_texts"])
            else:
                output = self.ocr.ocr(cropped_img)
                area.converted = " ".join(output[0]["rec_texts"])
            pass
        return entry
