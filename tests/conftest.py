import tempfile
from pathlib import Path

import pytest

from folioforge.models.document import DocumentReference
from folioforge.preprocessor.pdf import PDFPreprocessor


@pytest.fixture
def pdf_file():
    return Path(__file__).parent / "assets" / "test.pdf"


@pytest.fixture
def document_preprocessed(pdf_file: Path) -> DocumentReference:
    document = DocumentReference(path=pdf_file, items=[], converted=None)
    preprocessor = PDFPreprocessor()
    outdir = Path(tempfile.mkdtemp(prefix="folioforge"))
    document = preprocessor.process(document, outdir)
    assert document
    return document
