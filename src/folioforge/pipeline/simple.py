import tempfile
from functools import partial
from pathlib import Path
from typing import TypeVar

from folioforge.extraction.protocol import Extractor
from folioforge.models.document import DocumentReference
from folioforge.output.protocol import OutputGenerator
from folioforge.pipeline.protocol import PipelineExecutor
from folioforge.postprocessor.protocol import Postprocessor
from folioforge.preprocessor.protocol import Preprocessor

T = TypeVar("T")


class SimplePipelineExecutor[T](PipelineExecutor):
    def __init__(
        self,
        preprocessors: list[Preprocessor],
        extractor: Extractor,
        format: OutputGenerator[T],
        postprocessors: list[Postprocessor] | None,
        outdir: Path,
    ) -> None:
        self.preprocessors = preprocessors
        self.extractor = extractor
        self.format = format
        self.outdir = outdir
        self.postprocessors = postprocessors

    @classmethod
    def setup(
        cls,
        preprocessors: list[Preprocessor],
        extractor: Extractor,
        format: OutputGenerator[T],
        postprocessors: list[Postprocessor] | None = None,
        outdir: Path | None = None,
    ) -> "SimplePipelineExecutor":
        if outdir is None:
            outdir = Path(tempfile.mkdtemp(prefix="folioforge"))
        return SimplePipelineExecutor(preprocessors, extractor, format, postprocessors, outdir)

    def execute(self, paths: list[Path]) -> T:
        references = [DocumentReference(path=path, items=[], converted=None) for path in paths]

        for processor in self.preprocessors:
            references = list(filter(None, map(partial(processor.process, outdir=self.outdir), references)))
        for ref in references:
            ref.items = list(map(self.extractor.extract, ref.items))
            ref.converted = "\n\n".join(i.converted or "" for i in ref.items)
        if self.postprocessors:
            for postprocessor in self.postprocessors:
                references = list(postprocessor.process(references, self.outdir))
        return self.format.convert(references)
