from folioforge.models.document import DocumentReference
from folioforge.output.protocol import OutputGenerator


class PassthroughGenerator(OutputGenerator[str]):
    """Returns text as received from the underlying extractor."""

    def convert(self, document: list[DocumentReference]) -> list[tuple[DocumentReference, str]]:
        return [(d, d.converted or "") for d in document]
