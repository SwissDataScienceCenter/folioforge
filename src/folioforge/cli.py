from enum import Enum
from pathlib import Path
from typing import Annotated, Any

import typer

from folioforge.extraction.docling import DoclingExtractor
from folioforge.extraction.gemini import GeminiExtractor
from folioforge.extraction.ocr.paddle import PaddleOcrExtractor
from folioforge.extraction.protocol import Extractor
from folioforge.extraction.two_phase import TwoPhaseExtractor
from folioforge.output.html import HtmlGenerator
from folioforge.output.json import JsonGenerator
from folioforge.output.markdown import MarkdownGenerator
from folioforge.output.passthrough import PassthroughGenerator
from folioforge.output.protocol import OutputGenerator
from folioforge.pipeline.dask import DaskPipelineExecutor
from folioforge.pipeline.protocol import PipelineExecutor
from folioforge.pipeline.simple import SimplePipelineExecutor
from folioforge.postprocessor.debug import DebugPostprocessor
from folioforge.preprocessor.pdf import PDFPreprocessor
from folioforge.preprocessor.protocol import Preprocessor

app = typer.Typer()


class PipelineTypes(str, Enum):
    simple = "simple"
    dask = "dask"


class PreprocessorTypes(str, Enum):
    pdf = "pdf"
    pymupdf = "pymupdf"


class ExtractorTypes(str, Enum):
    docling = "docling"
    doclayout_yolo_doclaynet = "doclayout_yolo_doclaynet"
    doclayout_yolo_d4la = "doclayout_yolo_d4la"
    doclayout_yolo_docstructbench = "doclayout_yolo_docstructbench"
    marker = "marker"
    gemini = "gemini"


class OutputFormat(str, Enum):
    passthrough = "passthrough"
    markdown = "markdown"
    json = "json"
    html = "html"


def get_preprocessor():
    return [PreprocessorTypes.pdf]


@app.command()
def convert(
    paths: Annotated[list[Path], typer.Argument(help="path of PDFs to convert")],
    preprocessor: Annotated[
        list[PreprocessorTypes], typer.Option(default_factory=get_preprocessor, help="the preprocessor to use, can specify multiple")
    ],
    pipeline: Annotated[PipelineTypes, typer.Option(help="the pipeline executor")] = PipelineTypes.simple,
    extractor: Annotated[ExtractorTypes, typer.Option(help="the model to use")] = ExtractorTypes.docling,
    format: Annotated[OutputFormat, typer.Option(help="what format to create results in")] = OutputFormat.markdown,
    debug: Annotated[bool, typer.Option(help="turn on debug mode, stores annotated images in output folder")] = False,
    confidence: Annotated[float, typer.Option(help="the minimum confidence threshold for layout detection")] = 0.2,
    out: Annotated[Path | None, typer.Option(help="output folder, print to stdout if not supplied")] = None,
):
    """Convert PDF documents to text."""
    # optional imports

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
                case PreprocessorTypes.pymupdf:
                    try:
                        from folioforge.preprocessor.pdf import PymupdfPreprocessor
                    except ImportError as e:
                        raise ImportError("pymupdf preprocessor requires 'pymupdf' extra to be installed") from e

                    preprocessors.append(PymupdfPreprocessor())

    extractor_cls: type[Extractor]
    extractor_args: dict[str, Any] = {}
    match extractor:
        case ExtractorTypes.docling:
            extractor_cls = DoclingExtractor
            extractor_args["min_confidence"] = confidence
        case ExtractorTypes.doclayout_yolo_doclaynet:
            try:
                from folioforge.extraction.layout.doclayout_yolo import DoclayoutYOLODocLayNet
            except ImportError as e:
                raise ImportError("doclayout_yolo_doclaynet extractor requires 'doclayout_yolo' extra to be installed") from e

            extractor_cls = TwoPhaseExtractor
            extractor_args["layout_detector"] = DoclayoutYOLODocLayNet(min_confidence=confidence)
            extractor_args["ocr_extractor"] = PaddleOcrExtractor()
        case ExtractorTypes.doclayout_yolo_d4la:
            try:
                from folioforge.extraction.layout.doclayout_yolo import DoclayoutYOLOD4LA
            except ImportError as e:
                raise ImportError("doclayout_yolo_dl4a extractor requires 'doclayout_yolo' extra to be installed") from e

            extractor_cls = TwoPhaseExtractor
            extractor_args["layout_detector"] = DoclayoutYOLOD4LA(min_confidence=confidence)
            extractor_args["ocr_extractor"] = PaddleOcrExtractor()
        case ExtractorTypes.doclayout_yolo_docstructbench:
            try:
                from folioforge.extraction.layout.doclayout_yolo import DoclayoutYOLODocStructBench
            except ImportError as e:
                raise ImportError("doclayout_yolo_docstructbench extractor requires 'doclayout_yolo' extra to be installed") from e

            extractor_cls = TwoPhaseExtractor
            extractor_args["layout_detector"] = DoclayoutYOLODocStructBench(min_confidence=confidence)
            extractor_args["ocr_extractor"] = PaddleOcrExtractor()
        case ExtractorTypes.marker:
            try:
                from folioforge.extraction.marker import MarkerPDFExtractor
            except ImportError as e:
                raise ImportError("marker extractor requires 'marker' extra to be installed") from e

            extractor_cls = MarkerPDFExtractor
            extractor_args["min_confidence"] = confidence
        case ExtractorTypes.gemini:
            extractor_cls = GeminiExtractor

    format_cls: type[OutputGenerator]
    match format:
        case OutputFormat.passthrough:
            format_cls = PassthroughGenerator
        case OutputFormat.markdown:
            format_cls = MarkdownGenerator
        case OutputFormat.json:
            format_cls = JsonGenerator
        case OutputFormat.html:
            format_cls = HtmlGenerator

    postprocessors = None

    if debug:
        postprocessors = [DebugPostprocessor()]

    executor = executor_cls.setup(
        preprocessors=preprocessors, extractor=extractor_cls(**extractor_args), postprocessors=postprocessors, format=format_cls()
    )

    result = executor.execute(paths)
    if out is None:
        for r in result:
            print(r[1])
    else:
        out.mkdir(parents=True, exist_ok=True)
        for r in result:
            (out / r[0].path.stem).write_text(r[1])


def default_evaluation_extractors() -> list[ExtractorTypes]:
    # we exclude gemini because it's reeeeally slow
    return [e for e in ExtractorTypes if e != ExtractorTypes.gemini]


@app.command()
def evaluate(
    paths: Annotated[list[Path], typer.Argument()],
    preprocessor: Annotated[list[PreprocessorTypes], typer.Option(default_factory=get_preprocessor)],
    extractors: Annotated[list[ExtractorTypes], typer.Option(default_factory=default_evaluation_extractors)],
    pipeline: PipelineTypes = PipelineTypes.simple,
    output: Path = Path("output.html"),
):
    """Run a selection of models over a set of PDFs and create a report comparing the results."""
    evaluation_results = {t: [] for t in extractors}

    preprocessors: list[Preprocessor] = []
    if preprocessor is not None:
        for p in preprocessor:
            match p:
                case PreprocessorTypes.pdf:
                    preprocessors.append(PDFPreprocessor())

    for extractor, result in evaluation_results.items():
        print(f"Evaluating {extractor.value}...")
        extractor_cls: type[Extractor]
        extractor_args: dict[str, Any] = {}
        match extractor:
            case ExtractorTypes.docling:
                extractor_cls = DoclingExtractor
            case ExtractorTypes.doclayout_yolo_doclaynet:
                try:
                    from folioforge.extraction.layout.doclayout_yolo import DoclayoutYOLODocLayNet
                except ImportError as e:
                    raise ImportError("doclayout_yolo_doclaynet extractor requires 'doclayout_yolo' extra to be installed") from e

                extractor_cls = TwoPhaseExtractor
                extractor_args["layout_detector"] = DoclayoutYOLODocLayNet()
                extractor_args["ocr_extractor"] = PaddleOcrExtractor()
            case ExtractorTypes.doclayout_yolo_d4la:
                try:
                    from folioforge.extraction.layout.doclayout_yolo import DoclayoutYOLOD4LA
                except ImportError as e:
                    raise ImportError("doclayout_yolo_dl4a extractor requires 'doclayout_yolo' extra to be installed") from e

                extractor_cls = TwoPhaseExtractor
                extractor_args["layout_detector"] = DoclayoutYOLOD4LA()
                extractor_args["ocr_extractor"] = PaddleOcrExtractor()
            case ExtractorTypes.doclayout_yolo_docstructbench:
                try:
                    from folioforge.extraction.layout.doclayout_yolo import DoclayoutYOLODocStructBench
                except ImportError as e:
                    raise ImportError("doclayout_yolo_docstructbench extractor requires 'doclayout_yolo' extra to be installed") from e

                extractor_cls = TwoPhaseExtractor
                extractor_args["layout_detector"] = DoclayoutYOLODocStructBench()
                extractor_args["ocr_extractor"] = PaddleOcrExtractor()
            case ExtractorTypes.marker:
                try:
                    from folioforge.extraction.marker import MarkerPDFExtractor
                except ImportError as e:
                    raise ImportError("marker extractor requires 'marker' extra to be installed") from e

                extractor_cls = MarkerPDFExtractor
            case ExtractorTypes.gemini:
                extractor_cls = GeminiExtractor
        executor = SimplePipelineExecutor.setup(
            preprocessors=preprocessors, extractor=extractor_cls(**extractor_args), format=HtmlGenerator(full=False)
        )
        result.extend(executor.execute(paths))

    html = '<html><body><table border="1"><thead><tr><th></th>'
    for extractor in evaluation_results:
        html += f"<th>{extractor}</th>"
    html += "</tr></thead><tbody>"
    for row, path in enumerate(paths):
        html += f"<tr><td><bold>{path.name}</bold></td>"
        for result in evaluation_results.values():
            html += f"<td>{result[row]}</td>"
        html += f"<td><embed src='{path}' type='application/pdf' width='800' height='600' /></td>"
        html += "</tr>"
    html += "</tbody></table></body></html>"
    with open(output, "w") as f:
        f.write(html)
    print(f"Output written to {output}")
