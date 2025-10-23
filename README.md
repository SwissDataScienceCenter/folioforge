# folioforge

A library wrapping various PDF extraction tools with common workflows and tooling.

Currently supports Docling as well as the three DoclayoutYOLO models with PaddleOCR text recognition.

## Installation
for CLI use:

```bash
$ uv tool install git+https://github.com/SwissDataScienceCenter/folioforge
```

as a library:
```bash
$ uv add "folioforge @ git+https://github.com/SwissDataScienceCenter/folioforge"
```

## Usage

### CLI

```bash
$ folioforge convert myfile.pdf
```

```
 Usage: folioforge convert [OPTIONS] PATHS...

 Convert PDF documents to text.

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    paths      PATHS...  path of PDFs to convert [required]                                                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --preprocessor                  [pdf]                                               the preprocessor to use, can specify multiple       │
│                                                                                     [default: (dynamic)]                                │
│ --pipeline                      [simple|dask]                                       the pipeline executor [default: simple]             │
│ --extractor                     [docling|doclayout_yolo_doclaynet|doclayout_yolo_d  the model to use [default: docling]                 │
│                                 4la|doclayout_yolo_docstructbench]                                                                      │
│ --format                        [passthrough|markdown|json|html]                    what format to create results in                    │
│                                                                                     [default: markdown]                                 │
│ --debug           --no-debug                                                        turn on debug mode, stores annotated images in      │
│                                                                                     output folder                                       │
│                                                                                     [default: no-debug]                                 │
│ --confidence                    FLOAT                                               the minimum confidence threshold for layout         │
│                                                                                     detection                                           │
│                                                                                     [default: 0.2]                                      │
│ --help                                                                              Show this message and exit.                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Usage: folioforge evaluate [OPTIONS] PATHS...

 Run a selection of models over a set of PDFs and create a report comparing the results.

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    paths      PATHS...  [required]                                                                                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --preprocessor        [pdf]                                                    [default: (dynamic)]                                     │
│ --extractors          [docling|doclayout_yolo_doclaynet|doclayout_yolo_d4la|d  [default: (dynamic)]                                     │
│                       oclayout_yolo_docstructbench]                                                                                     │
│ --pipeline            [simple|dask]                                            [default: simple]                                        │
│ --output              PATH                                                     [default: output.html]                                   │
│ --help                                                                         Show this message and exit.                              │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### Library

```python
from folioforge.pipeline.simple import SimplePipelineExecutor
from folioforge.preprocessor.pdf import PDFPreprocessor
from folioforge.extraction.docling import DoclingExtractor
from folioforge.output.markdown import MarkdownGenerator

paths = ["myfile.pdf"]

pipeline = SimplePipelineExecutor.setup(preprocessors=[PDFPreprocessor()], extractor=DoclingExtractor(), format=MarkdownGenerator())
result = pipeline.execute(paths)
for r in result:
    print(r)

```
