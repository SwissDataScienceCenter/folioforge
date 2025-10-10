from functools import singledispatchmethod
from folioforge.models.document import DocumentReference, Text, Image, Heading, ListItem, Table
from folioforge.output.protocol import OutputGenerator


class MarkdownGenerator(OutputGenerator[list[str]]):
    def convert(self, documents: list[DocumentReference]) -> list[str]:
        return [self.to_markdown(d) for d in documents]

    def to_markdown(self, document: DocumentReference) -> str:
        result = []

        for entry in document.items:
            for area in entry.layout:
                result.append(self.convert_element(area))
            result.append("\n")

        return "\n".join(result)

    @singledispatchmethod
    def convert_element(self, value) -> str:
        raise NotImplementedError(f"Unsupported type {type(value)}")

    @convert_element.register
    def _(self, value: Text) -> str:
        return value.converted or ""

    @convert_element.register
    def _(self, value: Image) -> str:
        return "<image>"

    @convert_element.register
    def _(self, value: ListItem) -> str:
        return f"* {value.converted}"

    @convert_element.register
    def _(self, value: Heading) -> str:
        return "#" * value.level + (value.converted or "")

    @convert_element.register
    def _(self, value: Table) -> str:
        headers = value.headers
        cells = value.cells
        cells = sorted(cells, key=lambda h: (h.start_col, h.start_row))
        result = []
        max_len = max(len(c.converted or "") for c in cells)
        if headers:
            headers = sorted(headers, key=lambda h: (h.start_col, h.start_row))
            max_len = max(max([len(h.converted or "") for h in headers]), max_len)
            result.append("| " + "| ".join((h.converted or "").ljust(max_len + 1) for h in headers) + "|")
            result.append("| " + "| ".join("-" * (max_len + 1) for h in headers) + "|")

        current_row = cells[0].start_row
        current_line = ""
        for cell in cells:
            if cell.start_row != current_row:
                result.append(current_line + "|")
                current_line = ""
                current_row = cell.start_row
            current_line += "| " + (cell.converted or "").ljust(max_len + 1)
        result.append(current_line + "|")
        return "\n".join(result)
