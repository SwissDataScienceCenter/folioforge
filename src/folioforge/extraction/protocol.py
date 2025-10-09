from typing import Protocol

from folioforge.models.document import DocumentReference


class Extractor(Protocol):
    def extract(self, documents: list[DocumentReference]): ...
