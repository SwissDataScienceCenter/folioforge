from folioforge.models.document import DocumentReference
from folioforge.output.protocol import OutputGenerator


class PassthroughGenerator(OutputGenerator[list[str]]):
    """Returns text as received from the underlying extractor."""

    def convert(self, document: list[DocumentReference]) -> list[str]:
        return [d.converted or "" for d in document]
