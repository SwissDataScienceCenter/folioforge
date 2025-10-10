from pathlib import Path
from typing import TypeVar

from folioforge.extraction.protocol import Extractor
from folioforge.models.document import DocumentReference
from folioforge.output.protocol import OutputGenerator
from folioforge.pipeline.protocol import PipelineExecutor
from folioforge.preprocessor.protocol import Preprocessor

T = TypeVar("T")


class SimplePipelineExecutor[T](PipelineExecutor):
    def __init__(self, preprocessors: list[Preprocessor], extractor: Extractor, output: OutputGenerator[T]) -> None:
        self.preprocessors = preprocessors
        self.extractor = extractor
        self.output = output

    @classmethod
    def setup(cls, preprocessors: list[Preprocessor], extractor: Extractor, output: OutputGenerator[T]) -> "SimplePipelineExecutor":
        return SimplePipelineExecutor(preprocessors, extractor, output)

    def execute(self, paths: list[Path]) -> list[T]:
        references = [DocumentReference(path, [], None) for path in paths]

        for processor in self.preprocessors:
            references = list(filter(None, map(processor.process, references)))
        for ref in references:
            ref.items = list(map(self.extractor.extract, ref.items))
            ref.converted = "\n\n".join(i.converted or "" for i in ref.items)
        return self.output.convert(references)
