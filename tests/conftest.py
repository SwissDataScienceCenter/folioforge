from folioforge.models.document import DocumentReference
from folioforge.preprocessor.pdf import PDFPreprocessor
import pytest
from pathlib import Path


@pytest.fixture
def pdf_file():
    return Path(__file__).parent / "assets" / "test.pdf"


@pytest.fixture
def document_preprocessed(pdf_file: Path) -> DocumentReference:
    document = DocumentReference(path=pdf_file, items=[], converted=None)
    preprocessor = PDFPreprocessor()
    document = preprocessor.process(document)
    assert document
    return document
