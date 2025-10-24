import filecmp
import shutil
import tempfile
from pathlib import Path

from folioforge.models.document import DocumentReference
from folioforge.preprocessor.image import AutoBrightness, Grayscale, Threshold
from folioforge.preprocessor.pdf import PDFPreprocessor


def test_pdf_preprocessor(pdf_file: Path):
    preprocessor = PDFPreprocessor()
    outdir = Path(tempfile.mkdtemp(prefix="folioforge"))
    document = preprocessor.process(DocumentReference(path=pdf_file, items=[], converted=None), outdir)
    assert document
    assert document.items
    assert len(document.items) == 1
    assert document.items[0].path.name == "page0.png"
    assert document.items[0].path.parent.name == pdf_file.stem


def test_auto_brightness_preprocessor(document_preprocessed_lenna_dark: DocumentReference):
    modified_file = document_preprocessed_lenna_dark.items[0].path
    tmpdir = Path(tempfile.mkdtemp(prefix="folioforge"))
    original_file = tmpdir / f"{modified_file.stem}_copy{modified_file.suffix}"
    shutil.copyfile(modified_file, original_file)
    preprocessor = AutoBrightness(min_brightness=0.9)
    document = preprocessor.process(document_preprocessed_lenna_dark, Path("."))

    assert document
    assert len(document.items) == 1
    assert not filecmp.cmp(document.items[0].path, original_file)


def test_grayscale_preprocessor(document_preprocessed_lenna: DocumentReference):
    modified_file = document_preprocessed_lenna.items[0].path
    tmpdir = Path(tempfile.mkdtemp(prefix="folioforge"))
    original_file = tmpdir / f"{modified_file.stem}_copy{modified_file.suffix}"
    shutil.copyfile(modified_file, original_file)
    preprocessor = Grayscale()
    document = preprocessor.process(document_preprocessed_lenna, Path("."))

    assert document
    assert len(document.items) == 1
    assert not filecmp.cmp(document.items[0].path, original_file)


def test_threshold_preprocessor(document_preprocessed_lenna: DocumentReference):
    modified_file = document_preprocessed_lenna.items[0].path
    tmpdir = Path(tempfile.mkdtemp(prefix="folioforge"))
    original_file = tmpdir / f"{modified_file.stem}_copy{modified_file.suffix}"
    shutil.copyfile(modified_file, original_file)
    preprocessor = Threshold()
    document = preprocessor.process(document_preprocessed_lenna, Path("."))

    assert document
    assert len(document.items) == 1
    assert not filecmp.cmp(document.items[0].path, original_file)
