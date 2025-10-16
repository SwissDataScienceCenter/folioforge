from typing import Protocol

from folioforge.models.document import DocumentEntry


class Extractor(Protocol):
    supports_pickle: bool

    def extract(self, entry: DocumentEntry) -> DocumentEntry: ...
