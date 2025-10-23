from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

from folioforge.models.document import DocumentReference


class Postprocessor(Protocol):
    def process(self, documents: Iterator[DocumentReference], outdir: Path) -> Iterator[DocumentReference]: ...
