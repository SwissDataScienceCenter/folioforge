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

╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    paths      PATHS...  [required]                                                                                                       │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --preprocessor        [pdf]                                                     [default: (dynamic)]                                       │
│ --pipeline            [simple|dask]                                             [default: simple]                                          │
│ --extractor           [docling|doclayout_yolo_doclaynet|doclayout_yolo_d4la|do  [default: docling]                                         │
│                       clayout_yolo_docstructbench]                                                                                         │
│ --output              [passthrough|markdown|json|html]                          [default: markdown]                                        │
│ --help                                                                          Show this message and exit.                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Usage: folioforge evaluate [OPTIONS] PATHS...

╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    paths      PATHS...  [required]                                                                                                       │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --preprocessor        [pdf]                                                     [default: (dynamic)]                                       │
│ --extractors          [docling|doclayout_yolo_doclaynet|doclayout_yolo_d4la|do  [default: (dynamic)]                                       │
│                       clayout_yolo_docstructbench]                                                                                         │
│ --pipeline            [simple|dask]                                             [default: simple]                                          │
│ --output              PATH                                                      [default: output.html]                                     │
│ --help                                                                          Show this message and exit.                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

### Library

```python
from folioforge.pipeline.simple import SimplePipelineExecutor
from folioforge.preprocessor.pdf import PDFPreprocessor
from folioforge.extraction.docling import DoclingExtractor
from folioforge.output.markdown import MarkdownGenerator

paths = ["myfile.pdf"]

pipeline = SimplePipelineExecutor.setup(preprocessors=[PDFPreprocessor()], extractor=DoclingExtractor(), output=MarkdownGenerator())
result = pipeline.execute(paths)
for r in result:
    print(r)

```
