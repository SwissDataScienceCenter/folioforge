import tempfile
from pathlib import Path

import pymupdf

from folioforge.models.document import DocumentReference
from folioforge.preprocessor import Preprocessor


class PDFPreprocessor(Preprocessor):
    name = "pdf-preprocessor"

    def __init__(self, outdir: Path, filter_non_pdfs: bool = True) -> None:
        if outdir is None:
            outdir = tempfile.mkdtemp(prefix=self.name)

        self.outdir = outdir
        self.filter_non_pdfs = filter_non_pdfs

    def process(self, documents: list[DocumentReference]) -> list[DocumentReference]:
        new_documents = []

        for doc in documents:
            if doc.path.suffix != ".pdf" or len(doc.items) > 0:
                if not self.filter_non_pdfs:
                    new_documents.append(doc)
                continue

            pdf = pymupdf.open(doc.path)
            pages_dir = Path(f"{self.outdir}/{doc.path.stem}")
            pages_dir.mkdir(parents=True, exist_ok=True)
            for page_num, page in enumerate(pdf.pages()):
                image = page.get_pixmap(dpi=300, alpha=False)

                out_path = Path(f"/page{page_num}.png")
                image.save(out_path)
                doc.items.append(out_path)
            new_documents.append(doc)

        return new_documents
