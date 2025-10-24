import shutil
import tempfile
from pathlib import Path

import pytest

from folioforge.models.document import DocumentEntry, DocumentReference


@pytest.fixture
def pdf_file():
    return Path(__file__).parent / "assets" / "test.pdf"


@pytest.fixture
def image_file():
    tmpdir = Path(tempfile.mkdtemp(prefix="folioforge_image"))
    source = Path(__file__).parent / "assets" / "test.png"
    dest = tmpdir / "test.png"
    shutil.copyfile(source, dest)
    return dest


@pytest.fixture
def lenna_file():
    tmpdir = Path(tempfile.mkdtemp(prefix="folioforge_image"))
    source = Path(__file__).parent / "assets" / "lenna.png"
    dest = tmpdir / "test.png"
    shutil.copyfile(source, dest)
    return dest


@pytest.fixture
def lenna_dark_file():
    tmpdir = Path(tempfile.mkdtemp(prefix="folioforge_image"))
    source = Path(__file__).parent / "assets" / "lenna_dark.png"
    dest = tmpdir / "test.png"
    shutil.copyfile(source, dest)
    return dest


@pytest.fixture
def document_preprocessed(pdf_file: Path, image_file: Path) -> DocumentReference:
    document = DocumentReference(path=pdf_file, items=[DocumentEntry(path=image_file, layout=[], converted=None)], converted=None)
    return document


@pytest.fixture
def document_preprocessed_lenna(pdf_file: Path, lenna_file: Path) -> DocumentReference:
    document = DocumentReference(path=pdf_file, items=[DocumentEntry(path=lenna_file, layout=[], converted=None)], converted=None)
    return document


@pytest.fixture
def document_preprocessed_lenna_dark(pdf_file: Path, lenna_dark_file: Path) -> DocumentReference:
    document = DocumentReference(path=pdf_file, items=[DocumentEntry(path=lenna_dark_file, layout=[], converted=None)], converted=None)
    return document
