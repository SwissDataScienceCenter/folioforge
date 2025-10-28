from functools import singledispatchmethod
from itertools import groupby

from folioforge.models.document import Area, DocumentReference, Heading, Image, ListItem, Table, Text
from folioforge.output.protocol import OutputGenerator


class MarkdownGenerator(OutputGenerator[str]):
    def convert(self, documents: list[DocumentReference]) -> list[tuple[DocumentReference, str]]:
        return [(d, self.to_markdown(d)) for d in documents]

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
        if not value.path:
            return "<image>"
        return f"![image]({value.path.resolve().as_uri()})"

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

        if not cells and not headers:
            return value.converted or ""

        cells = sorted(cells, key=lambda h: (h.start_row, h.start_col))
        result = []
        num_cols = max(c.end_col for c in headers + cells)
        max_len = [1] * (num_cols + 1)

        for cell in headers + cells:
            text_len = len(cell.converted or "")
            if text_len > max_len[cell.start_col]:
                max_len[cell.start_col] = text_len

        if headers:
            headers = sorted(headers, key=lambda h: (h.start_row, h.start_col))
            current_row = headers[0].start_row
            for _, group in groupby(headers, key=lambda h: h.start_row):
                result.append("| " + "| ".join((h.converted or "").ljust(max_len[h.start_col] + 1) for h in group) + "|")
            result.append("| " + " | ".join("-" * (max_len[h.start_col]) for h in headers) + " |")

        if cells:
            current_row = cells[0].start_row
            current_line = ""
            for cell in cells:
                if cell.start_row != current_row:
                    result.append(current_line + "|")
                    current_line = ""
                    current_row = cell.start_row
                current_line += "| " + (cell.converted or "").ljust(max_len[cell.start_col] + 1)
            result.append(current_line + "|")
        return "\n".join(result)

    @convert_element.register
    def _(self, value: Area) -> str:
        return value.converted or ""
