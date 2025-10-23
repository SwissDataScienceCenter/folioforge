from typing import Protocol

from folioforge.models.document import DocumentEntry


class Extractor(Protocol):
    supports_pickle: bool

    def __init__(self, min_confidence: float = 0.2) -> None: ...

    def extract(self, entry: DocumentEntry) -> DocumentEntry: ...
