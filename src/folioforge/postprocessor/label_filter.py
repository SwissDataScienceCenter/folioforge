from collections.abc import Iterator
from pathlib import Path

from folioforge.models.document import DocumentReference
from folioforge.models.labels import Label
from folioforge.postprocessor.protocol import Postprocessor


class LabelFilter(Postprocessor):
    """Filters out elements based on labels."""

    def __init__(self, keep: list[Label] | None = None, discard: list[Label] | None = None) -> None:
        self.keep = keep
        self.discard = discard

    def process(self, documents: Iterator[DocumentReference], outdir: Path) -> Iterator[DocumentReference]:
        for document in documents:
            for item in document.items:
                if self.keep is not None:
                    item.layout = [area for area in item.layout if area.label in self.keep]
                if self.discard is not None:
                    item.layout = [area for area in item.layout if area.label not in self.discard]

            yield document
