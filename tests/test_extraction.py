from folioforge.extraction.docling import DoclingExtractor
from folioforge.extraction.layout.doclayout_yolo import DoclayoutYOLOD4LA
from folioforge.extraction.ocr.paddle import PaddleOcrExtractor
from folioforge.extraction.two_phase import TwoPhaseExtractor
from folioforge.models.document import DocumentReference


def test_docling(document_preprocessed: DocumentReference):
    extractor = DoclingExtractor()
    entry = extractor.extract(document_preprocessed.items[0])
    assert entry
    assert entry.converted
    assert "## This is a test PDF document" in entry.converted
    assert "If you can read this, you have Adobe Acrobat Reader installed on your computer" in entry.converted


def test_doclayout_yolo(document_preprocessed: DocumentReference):
    extractor = TwoPhaseExtractor(layout_detector=DoclayoutYOLOD4LA(), ocr_extractor=PaddleOcrExtractor())
    entry = extractor.extract(document_preprocessed.items[0])
    assert entry
    assert (
        entry.converted == "This is a test PDF document.\nIf you can read this, you have Adobe Acrobat Reader installed on your computer."
    )
