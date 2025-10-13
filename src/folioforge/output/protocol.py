from typing import Protocol, TypeVar

from folioforge.models.document import DocumentReference

T = TypeVar("T")


class OutputGenerator[T](Protocol):
    def convert(self, documents: list[DocumentReference]) -> T: ...
