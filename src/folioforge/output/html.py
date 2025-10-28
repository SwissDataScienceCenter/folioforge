from functools import singledispatchmethod

from folioforge.models.document import DocumentReference, Heading, Image, ListItem, Table
from folioforge.output.protocol import OutputGenerator


class HtmlGenerator(OutputGenerator[str]):
    def __init__(self, full: bool = True) -> None:
        self.full = full
        self.in_list = False

    def convert(self, documents: list[DocumentReference]) -> list[tuple[DocumentReference, str]]:
        return [(d, self.to_html(d)) for d in documents]

    def to_html(self, document: DocumentReference) -> str:
        output = "<html><body>" if self.full else ""
        for item in document.items:
            for area in item.layout:
                output += self.convert_area(area)
        output += "</body></html>" if self.full else ""
        return output

    @singledispatchmethod
    def convert_area(self, area) -> str:
        prefix = "</ul>" if self.in_list else ""
        self.in_list = False
        return f"{prefix}\n<p>{area.converted}</p>\n"

    @convert_area.register
    def _(self, area: Heading) -> str:
        prefix = "</ul>" if self.in_list else ""
        self.in_list = False
        return f"{prefix}\n<h{area.level}>{area.converted}</h{area.level}>\n"

    @convert_area.register
    def _(self, area: ListItem) -> str:
        prefix = "" if self.in_list else "<ul>"
        self.in_list = True
        return f"{prefix}\n<li>{area.converted}</li>\n"

    @convert_area.register
    def _(self, area: Image) -> str:
        prefix = "</ul>" if self.in_list else ""
        self.in_list = False
        if not area.path:
            return f"{prefix}\n{{image}}\n"
        return f"{prefix}\n<img src='{area.path.resolve().as_uri()}' />\n"

    @convert_area.register
    def _(self, area: Table) -> str:
        output = "</ul>\n<table border='0.5'>" if self.in_list else "<table border='0.5'>"
        self.in_list = False
        if area.headers:
            output += "<thead><tr>" + "".join(f"<th>{h.converted}</th>" for h in area.headers) + "</tr></thead>"
        output += "<tbody>"
        current_row = -1
        cells = sorted(area.cells, key=lambda c: (c.start_row, c.start_col))
        for cell in cells:
            if cell.start_row != current_row and current_row == -1:
                output += "<tr>"
            elif cell.start_row != current_row:
                output += "</tr><tr>"
            output += f"<td colspan={cell.col_span} rowspan={cell.row_span}>{cell.converted}</td>"
            current_row = cell.start_row
        output += "</tr></tbody></table>"

        return output
