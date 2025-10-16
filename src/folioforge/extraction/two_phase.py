from folioforge.extraction.layout.protocol import LayoutDetector
from folioforge.extraction.ocr.protocol import OcrExtractor
from folioforge.extraction.protocol import Extractor
from folioforge.models.document import DocumentEntry


class TwoPhaseExtractor(Extractor):
    """An extractor that does layout detection and ocr phases separately."""

    def __init__(self, layout_detector: LayoutDetector, ocr_extractor: OcrExtractor) -> None:
        self.layout_detector = layout_detector
        self.ocr_extractor = ocr_extractor
        self.supports_pickle = self.layout_detector.supports_pickle and self.ocr_extractor.supports_pickle

    def extract(self, entry: DocumentEntry) -> DocumentEntry:
        entry = self.layout_detector.detect(entry)
        entry = self.ocr_extractor.extract(entry)
        return entry
