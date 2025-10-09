from pathlib import Path
from typing import Protocol, TypeVar

from folioforge.extraction.protocol import Extractor
from folioforge.models.document import DocumentReference
from folioforge.preprocessor.protocol import Preprocessor

T = TypeVar("T", bound="PipelineExecutor")


class PipelineExecutor(Protocol):
    @classmethod
    def setup(cls: type[T], preprocessors: list[Preprocessor], extractors: list[Extractor]) -> T: ...
    def execute(self, paths: list[Path]) -> list[DocumentReference]: ...
