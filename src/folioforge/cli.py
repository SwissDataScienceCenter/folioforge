from dataclasses import asdict
from pathlib import Path
from typing import Annotated

from folioforge.pipeline.dask import DaskPipelineExecutor
import typer

from folioforge.extraction.docling import DoclingExtractor
from folioforge.pipeline.simple import SimplePipelineExecutor
from folioforge.preprocessor.pdf import PDFPreprocessor

app = typer.Typer()


@app.command()
def main(paths: Annotated[list[Path], typer.Argument()]):
    # pipeline = SimplePipelineExecutor.setup(preprocessors=[PDFPreprocessor()], extractor=DoclingExtractor())

    pipeline = DaskPipelineExecutor.setup(preprocessors=[PDFPreprocessor()], extractor=DoclingExtractor())
    result = pipeline.execute(paths)
    for r in result:
        print(r.converted)
