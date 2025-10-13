from pathlib import Path
from typing import Annotated

import typer

from folioforge.extraction.docling import DoclingExtractor
from folioforge.output.passthrough import PassthroughGenerator
from folioforge.pipeline.simple import SimplePipelineExecutor
from folioforge.preprocessor.pdf import PDFPreprocessor

app = typer.Typer()


@app.command()
def main(paths: Annotated[list[Path], typer.Argument()]):
    pipeline = SimplePipelineExecutor.setup(preprocessors=[PDFPreprocessor()], extractor=DoclingExtractor(), output=PassthroughGenerator())

    # pipeline = DaskPipelineExecutor.setup(preprocessors=[PDFPreprocessor()], extractor=DoclingExtractor())
    result = pipeline.execute(paths)
    for r in result:
        print(r)
