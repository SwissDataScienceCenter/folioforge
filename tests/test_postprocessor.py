import filecmp
import tempfile
from pathlib import Path

import pytest

from folioforge.models.document import BoundingBox, DocumentEntry, DocumentReference, Heading, Image, Table, Text
from folioforge.models.labels import Label
from folioforge.postprocessor.debug import DebugPostprocessor
from folioforge.postprocessor.label_filter import LabelFilter


@pytest.fixture
def documents() -> list[DocumentReference]:
    bbox = BoundingBox(x0=0, y0=0, x1=1, y1=1)
    return [
        DocumentReference(
            path=Path("."),
            items=[
                DocumentEntry(
                    path=Path("."),
                    layout=[
                        Text(bbox=bbox, label=Label.TEXT, confidence=0.2, converted=None),
                        Heading(bbox=bbox, label=Label.PAGE_HEADER, confidence=0.2, converted=None, level=1),
                        Image(bbox=bbox, label=Label.IMAGE, confidence=0.2, converted=None),
                        Table(bbox=bbox, label=Label.TABLE, confidence=0.2, converted=None, headers=[], cells=[]),
                        Text(bbox=bbox, label=Label.TEXT, confidence=0.2, converted=None),
                    ],
                    converted=None,
                )
            ],
            converted=None,
        )
    ]


def test_label_filter_keep(documents: list[DocumentReference]):
    filter = LabelFilter(keep=[Label.TEXT])
    filtered = list(filter.process(documents, outdir=Path(".")))
    assert filtered
    assert len(filtered) == 1
    assert len(filtered[0].items) == 1
    assert len(filtered[0].items[0].layout) == 2
    assert all(i.label == Label.TEXT for i in filtered[0].items[0].layout)


def test_label_filter_discard(documents: list[DocumentReference]):
    filter = LabelFilter(discard=[Label.TEXT])
    filtered = list(filter.process(documents, outdir=Path(".")))
    assert filtered
    assert len(filtered) == 1
    assert len(filtered[0].items) == 1
    assert len(filtered[0].items[0].layout) == 3
    assert not any(i.label == Label.TEXT for i in filtered[0].items[0].layout)


def test_debug_filter(document_preprocessed: DocumentReference):
    processor = DebugPostprocessor()
    outdir = Path(tempfile.mkdtemp(prefix="folioforge"))
    document_preprocessed.items[0].layout.append(
        Text(bbox=BoundingBox(x0=10, y0=10, x1=100, y1=100), label=Label.TEXT, confidence=0.5, converted="")
    )
    documents = list(processor.process([document_preprocessed], outdir=outdir))
    assert documents
    assert len(documents) == 1
    assert len(documents[0].items) == 1
    assert len(documents[0].items[0].layout) == 1
    result = outdir / documents[0].path.stem / "debug" / documents[0].items[0].path.name
    assert result.exists()
    assert not filecmp.cmp(documents[0].items[0].path, result)
