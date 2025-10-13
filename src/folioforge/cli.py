from enum import Enum
from pathlib import Path
from typing import Annotated, Any

from folioforge.extraction.layout.doclayout_yolo import DoclayoutYOLODocLayNet
from folioforge.extraction.ocr.paddle import PaddleOcrExtractor
from folioforge.extraction.protocol import Extractor
from folioforge.extraction.two_phase import TwoPhaseExtractor
import typer

from folioforge.extraction.docling import DoclingExtractor
from folioforge.output.json import JsonGenerator
from folioforge.output.markdown import MarkdownGenerator
from folioforge.output.passthrough import PassthroughGenerator
from folioforge.output.protocol import OutputGenerator
from folioforge.pipeline.dask import DaskPipelineExecutor
from folioforge.pipeline.protocol import PipelineExecutor
from folioforge.pipeline.simple import SimplePipelineExecutor
from folioforge.preprocessor.pdf import PDFPreprocessor
from folioforge.preprocessor.protocol import Preprocessor

app = typer.Typer()


class PipelineTypes(str, Enum):
    simple = "simple"
    dask = "dask"


class PreprocessorTypes(str, Enum):
    pdf = "pdf"


class ExtractorTypes(str, Enum):
    docling = "docling"
    doclayout_yolo = "doclayout_yolo"


class OutputTypes(str, Enum):
    passthrough = "passthrough"
    markdown = "markdown"
    json = "json"


def get_preprocessor():
    return [PreprocessorTypes.pdf]


@app.command()
def main(
    paths: Annotated[list[Path], typer.Argument()],
    preprocessor: Annotated[list[PreprocessorTypes], typer.Option(default_factory=get_preprocessor)],
    pipeline: PipelineTypes = PipelineTypes.simple,
    extractor: ExtractorTypes = ExtractorTypes.docling,
    output: OutputTypes = OutputTypes.markdown,
):
    executor_cls: type[PipelineExecutor]
    match pipeline:
        case PipelineTypes.simple:
            executor_cls = SimplePipelineExecutor
        case PipelineTypes.dask:
            executor_cls = DaskPipelineExecutor

    preprocessors: list[Preprocessor] = []
    if preprocessor is not None:
        for p in preprocessor:
            match p:
                case PreprocessorTypes.pdf:
                    preprocessors.append(PDFPreprocessor())

    extractor_cls: type[Extractor]
    extractor_args: dict[str, Any] = {}
    match extractor:
        case ExtractorTypes.docling:
            extractor_cls = DoclingExtractor
        case ExtractorTypes.doclayout_yolo:
            extractor_cls = TwoPhaseExtractor
            extractor_args["layout_detector"] = DoclayoutYOLODocLayNet()
            extractor_args["ocr_extractor"] = PaddleOcrExtractor()

    output_cls: type[OutputGenerator]
    match output:
        case OutputTypes.passthrough:
            output_cls = PassthroughGenerator
        case OutputTypes.markdown:
            output_cls = MarkdownGenerator
        case OutputTypes.json:
            output_cls = JsonGenerator

    executor = executor_cls.setup(preprocessors=preprocessors, extractor=extractor_cls(**extractor_args), output=output_cls())

    result = executor.execute(paths)
    for r in result:
        print(r)
