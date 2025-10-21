from pathlib import Path

import pytest

from folioforge.models.document import Area, BoundingBox, DocumentEntry, DocumentReference, Heading, Image, ListItem, Table, TableCell, Text
from folioforge.models.labels import Label
from folioforge.output.html import HtmlGenerator
from folioforge.output.json import JsonGenerator
from folioforge.output.markdown import MarkdownGenerator
from folioforge.output.passthrough import PassthroughGenerator


@pytest.fixture
def parsed_document():
    document = DocumentReference(
        path=Path(""),
        items=[
            DocumentEntry(
                path=Path(""),
                layout=[
                    Area(bbox=BoundingBox(x0=0, y0=0, x1=1, y1=1), label=Label.OTHER, confidence=1, converted="Other"),
                    Text(bbox=BoundingBox(x0=1, y0=0, x1=1, y1=1), label=Label.TEXT, confidence=1, converted="Text"),
                    Image(bbox=BoundingBox(x0=1, y0=1, x1=2, y1=2), label=Label.IMAGE, confidence=1, converted=None),
                    Heading(
                        bbox=BoundingBox(x0=2, y0=2, x1=3, y1=3), label=Label.PAGE_HEADER, confidence=1, converted="Page Header", level=1
                    ),
                    Heading(
                        bbox=BoundingBox(x0=3, y0=3, x1=4, y1=4),
                        label=Label.SECTION_HEADER,
                        confidence=1,
                        converted="Section Header",
                        level=2,
                    ),
                    ListItem(bbox=BoundingBox(x0=4, y0=4, x1=5, y1=5), label=Label.LIST_ITEM, confidence=1, converted="List1"),
                    ListItem(bbox=BoundingBox(x0=5, y0=5, x1=6, y1=6), label=Label.LIST_ITEM, confidence=1, converted="List2"),
                    Table(
                        bbox=BoundingBox(x0=6, y0=6, x1=7, y1=7),
                        label=Label.TABLE,
                        confidence=1,
                        converted="Table",
                        headers=[
                            TableCell(
                                bbox=None, row_span=1, col_span=1, start_row=1, start_col=1, end_row=2, end_col=1, converted="Header1"
                            ),
                            TableCell(
                                bbox=None, row_span=1, col_span=1, start_row=1, start_col=2, end_row=2, end_col=2, converted="Header2"
                            ),
                        ],
                        cells=[
                            TableCell(
                                bbox=None, row_span=1, col_span=1, start_row=2, start_col=1, end_row=3, end_col=1, converted="Cell11"
                            ),
                            TableCell(
                                bbox=None, row_span=1, col_span=1, start_row=2, start_col=2, end_row=3, end_col=2, converted="Cell12"
                            ),
                            TableCell(
                                bbox=None, row_span=1, col_span=1, start_row=3, start_col=1, end_row=4, end_col=1, converted="Cell21"
                            ),
                            TableCell(
                                bbox=None, row_span=1, col_span=1, start_row=3, start_col=2, end_row=4, end_col=2, converted="Cell22"
                            ),
                        ],
                    ),
                ],
                converted=None,
            )
        ],
        converted="passthrough text",
    )
    return document


def test_markup(parsed_document: DocumentReference):
    generator = MarkdownGenerator()
    result = generator.convert([parsed_document])
    content = result[0]
    assert (
        content
        == """Other
Text
<image>
#Page Header
##Section Header
* List1
* List2
| Header1 | Header2 |
| ------- | ------- |
| Cell11  | Cell12  |
| Cell21  | Cell22  |

"""
    )


def test_json(parsed_document: DocumentReference):
    generator = JsonGenerator()
    result = generator.convert([parsed_document])
    content = result[0]
    assert content == (
        '{"path":".","items":[{"path":".","layout":[{"bbox":{"x0":0.0,"y0":0.0,"x1":1.0,"y1":1.0},"label":"OTHER",'
        '"confidence":1.0,"converted":"Other"},{"bbox":{"x0":1.0,"y0":0.0,"x1":1.0,"y1":1.0},"label":"TEXT",'
        '"confidence":1.0,"converted":"Text"},{"bbox":{"x0":1.0,"y0":1.0,"x1":2.0,"y1":2.0},"label":"IMAGE",'
        '"confidence":1.0,"converted":null},{"bbox":{"x0":2.0,"y0":2.0,"x1":3.0,"y1":3.0},"label":"PAGE_HEADER",'
        '"confidence":1.0,"converted":"Page Header","level":1},{"bbox":{"x0":3.0,"y0":3.0,"x1":4.0,"y1":4.0},'
        '"label":"SECTION_HEADER","confidence":1.0,"converted":"Section Header","level":2},'
        '{"bbox":{"x0":4.0,"y0":4.0,"x1":5.0,"y1":5.0},"label":"LIST_ITEM","confidence":1.0,"converted":"List1"},'
        '{"bbox":{"x0":5.0,"y0":5.0,"x1":6.0,"y1":6.0},"label":"LIST_ITEM","confidence":1.0,"converted":"List2"},'
        '{"bbox":{"x0":6.0,"y0":6.0,"x1":7.0,"y1":7.0},"label":"TABLE","confidence":1.0,"converted":"Table",'
        '"headers":[{"bbox":null,"row_span":1,"col_span":1,"start_row":1,"end_row":2,"start_col":1,"end_col":1,'
        '"converted":"Header1"},{"bbox":null,"row_span":1,"col_span":1,"start_row":1,"end_row":2,"start_col":2,'
        '"end_col":2,"converted":"Header2"}],"cells":[{"bbox":null,"row_span":1,"col_span":1,"start_row":2,'
        '"end_row":3,"start_col":1,"end_col":1,"converted":"Cell11"},{"bbox":null,"row_span":1,"col_span":1,'
        '"start_row":2,"end_row":3,"start_col":2,"end_col":2,"converted":"Cell12"},{"bbox":null,"row_span":1,'
        '"col_span":1,"start_row":3,"end_row":4,"start_col":1,"end_col":1,"converted":"Cell21"},'
        '{"bbox":null,"row_span":1,"col_span":1,"start_row":3,"end_row":4,"start_col":2,"end_col":2,'
        '"converted":"Cell22"}]}],"converted":null}],"converted":"passthrough text"}'
    )


def test_html(parsed_document: DocumentReference):
    generator = HtmlGenerator()
    result = generator.convert([parsed_document])
    content = result[0]
    assert content == (
        "<html><body>\n<p>Other</p>\n\n<p>Text</p>\n\n{image}\n\n<h1>Page Header</h1>\n\n<h2>Section Header</h2>\n"
        "<ul>\n<li>List1</li>\n\n<li>List2</li>\n</ul>\n<table border='0.5'><thead><tr><th>Header1</th><th>Header2"
        "</th></tr></thead><tbody><tr><td colspan=1 rowspan=1>Cell11</td><td colspan=1 rowspan=1>Cell12</td></tr>"
        "<tr><td colspan=1 rowspan=1>Cell21</td><td colspan=1 rowspan=1>Cell22</td></tr></tbody></table></body>"
        "</html>"
    )


def test_passthrough(parsed_document: DocumentReference):
    generator = PassthroughGenerator()
    result = generator.convert([parsed_document])
    content = result[0]
    assert content == "passthrough text"
