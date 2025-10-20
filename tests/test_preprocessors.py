from pathlib import Path
from folioforge.models.document import DocumentReference
from folioforge.preprocessor.pdf import PDFPreprocessor


def test_pdf_preprocessor(pdf_file: Path):
    preprocessor = PDFPreprocessor()
    document = preprocessor.process(DocumentReference(path=pdf_file, items=[], converted=None))
    assert document
    assert document.items
    assert len(document.items) == 1
    assert document.items[0].path.name == "page0.png"
    assert document.items[0].path.parent.name == pdf_file.stem
