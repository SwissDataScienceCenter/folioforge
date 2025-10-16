from typing import Protocol

from folioforge.models.document import DocumentEntry


class LayoutDetector(Protocol):
    supports_pickle: bool

    def detect(self, document: DocumentEntry) -> DocumentEntry: ...
