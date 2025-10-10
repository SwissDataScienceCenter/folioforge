from pathlib import Path

from folioforge.extraction.protocol import Extractor
from folioforge.models.document import DocumentReference
from folioforge.pipeline.protocol import PipelineExecutor
from folioforge.preprocessor.protocol import Preprocessor


class SimplePipelineExecutor(PipelineExecutor):
    def __init__(self, preprocessors: list[Preprocessor], extractor: Extractor) -> None:
        self.preprocessors = preprocessors
        self.extractor = extractor

    @classmethod
    def setup(cls, preprocessors: list[Preprocessor], extractor: Extractor) -> "SimplePipelineExecutor":
        return SimplePipelineExecutor(preprocessors, extractor)

    def execute(self, paths: list[Path]) -> list[DocumentReference]:
        references = [DocumentReference(path, [], None) for path in paths]

        for processor in self.preprocessors:
            references = list(filter(None, map(processor.process, references)))
        for ref in references:
            ref.items = list(map(self.extractor.extract, ref.items))
            ref.converted = "\n\n".join(i.converted or "" for i in ref.items)
        return references
