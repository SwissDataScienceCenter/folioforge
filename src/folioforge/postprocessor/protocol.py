from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

from folioforge.models.document import DocumentReference


class Postprocessor(Protocol):
    def process(self, documents: Iterable[DocumentReference], outdir: Path) -> Iterable[DocumentReference]: ...
