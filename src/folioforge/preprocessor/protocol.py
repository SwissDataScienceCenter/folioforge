from typing import Protocol

from folioforge.models.document import DocumentReference


class Preprocessor(Protocol):
    """Preprocesses documents, potentially modifying them or parsing them to individual items."""

    def process(self, document: DocumentReference) -> DocumentReference | None: ...
