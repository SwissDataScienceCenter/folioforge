from typing import Protocol

from folioforge.models.document import DocumentEntry


class Extractor(Protocol):
    def extract(self, entry: DocumentEntry) -> DocumentEntry: ...
