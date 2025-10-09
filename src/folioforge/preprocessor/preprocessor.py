from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class DocumentReference:
    path: Path
    items: list[Path]


class Preprocessor(Protocol):
    """Preprocesses documents, potentially modifying them or parsing them to individual items."""

    def parse(self, documents: list[Path]) -> list[DocumentReference]: ...

    def process(
        self, documents: list[DocumentReference]
    ) -> list[DocumentReference]: ...
