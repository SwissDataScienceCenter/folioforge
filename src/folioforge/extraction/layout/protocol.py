from typing import Protocol

from folioforge.models.document import DocumentEntry


class LayoutDetector(Protocol):
    def detect(self, document: DocumentEntry) -> DocumentEntry: ...
