from typing import Protocol

from folioforge.models.document import DocumentEntry


class OcrExtractor(Protocol):
    def extract(self, document: DocumentEntry) -> DocumentEntry: ...
