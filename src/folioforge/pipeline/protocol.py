from pathlib import Path
from typing import Protocol, TypeVar

from folioforge.extraction.protocol import Extractor
from folioforge.output.protocol import OutputGenerator
from folioforge.postprocessor.protocol import Postprocessor
from folioforge.preprocessor.protocol import Preprocessor

T = TypeVar("T", bound="PipelineExecutor")
P = TypeVar("P")


class PipelineExecutor[P](Protocol):
    @classmethod
    def setup(
        cls: type[T],
        preprocessors: list[Preprocessor],
        extractors: list[Extractor],
        format: OutputGenerator[P],
        postprocessors: list[Postprocessor] | None = None,
        outdir: Path | None = None,
    ) -> T: ...
    def execute(self, paths: list[Path]) -> list[P]: ...
