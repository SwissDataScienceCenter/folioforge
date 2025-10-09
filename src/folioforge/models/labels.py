from enum import IntEnum


class Label(IntEnum):
    CAPTION = 0
    FOOTNOTE = 1
    LIST_ITEM = 2
    PAGE_FOOTER = 3
    PAGE_HEADER = 4
    IMAGE = 5
    SECTION_HEADER = 6
    TABLE = 7
    TEXT = 8
    TITLE = 9
    OTHER = 10
