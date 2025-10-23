from pathlib import Path

import pytest

from folioforge.models.document import DocumentEntry, DocumentReference


@pytest.fixture
def pdf_file():
    return Path(__file__).parent / "assets" / "test.pdf"


@pytest.fixture
def image_file():
    return Path(__file__).parent / "assets" / "test.png"


@pytest.fixture
def document_preprocessed(pdf_file: Path, image_file: Path) -> DocumentReference:
    document = DocumentReference(path=pdf_file, items=[DocumentEntry(path=image_file, layout=[], converted=None)], converted=None)
    return document
