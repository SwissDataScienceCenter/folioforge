from pathlib import Path

import pymupdf

from folioforge.models.document import DocumentEntry, DocumentReference
from folioforge.preprocessor.protocol import Preprocessor


class PDFPreprocessor(Preprocessor):
    def __init__(self, filter_non_pdfs: bool = True) -> None:
        self.filter_non_pdfs = filter_non_pdfs

    def process(self, document: DocumentReference, outdir: Path) -> DocumentReference | None:
        if document.path.suffix != ".pdf" or len(document.items) > 0:
            if self.filter_non_pdfs:
                return None
            return document

        pdf = pymupdf.open(document.path)
        pages_dir = Path(f"{outdir}/{document.path.stem}")
        pages_dir.mkdir(parents=True, exist_ok=True)
        items = []
        for page_num, page in enumerate(pdf.pages()):
            image = page.get_pixmap(dpi=300, alpha=False)

            out_path = pages_dir / f"page{page_num}.png"
            image.save(out_path)
            items.append(DocumentEntry(path=out_path, layout=[], converted=None))
        return DocumentReference(path=document.path, items=items, converted=None)
