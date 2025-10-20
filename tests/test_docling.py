from folioforge.models.document import DocumentReference
from folioforge.extraction.docling import DoclingExtractor


def test_docling(document_preprocessed: DocumentReference):
    extractor = DoclingExtractor()
    entry = extractor.extract(document_preprocessed.items[0])
    assert entry
    assert (
        entry.converted
        == "## This is a test PDF document.\n\nIf you can read this; you have Adobe Acrobat Reader installed on your computer ."
    )
