from folioforge.models.document import DocumentReference
from folioforge.output.protocol import OutputGenerator


class JsonGenerator(OutputGenerator[str]):
    def convert(self, documents: list[DocumentReference]) -> list[tuple[DocumentReference, str]]:
        result = []
        for doc in documents:
            result.append((doc, doc.model_dump_json(indent=2)))
        return result
