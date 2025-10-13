from dataclasses import asdict
from typing import Any

from folioforge.models.document import DocumentReference
from folioforge.output.protocol import OutputGenerator


class JsonOutput(OutputGenerator[list[dict[str, Any]]]):
    def convert(self, documents: list[DocumentReference]) -> list[dict[str, Any]]:
        result = []
        for doc in documents:
            result.append(asdict(doc))
        return result
