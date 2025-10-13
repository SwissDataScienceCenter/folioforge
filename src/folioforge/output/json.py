from dataclasses import asdict
import json
from typing import Any

from folioforge.models.document import DocumentReference
from folioforge.output.protocol import OutputGenerator


class JsonGenerator(OutputGenerator[list[str]]):
    def convert(self, documents: list[DocumentReference]) -> list[str]:
        result = []
        for doc in documents:
            result.append(json.dumps(asdict(doc)))
        return result
