from collections.abc import Iterator
from pathlib import Path

import cv2

from folioforge.models.document import DocumentReference
from folioforge.models.labels import Label
from folioforge.postprocessor.protocol import Postprocessor


def _label_to_color(label: Label) -> tuple[int, int, int]:
    match label:
        case Label.TITLE:
            return (173, 35, 35)
        case Label.PAGE_HEADER:
            return (42, 75, 215)
        case Label.SECTION_HEADER:
            return (29, 105, 20)
        case Label.LIST_ITEM:
            return (129, 74, 25)
        case Label.PAGE_FOOTER:
            return (129, 38, 192)
        case Label.IMAGE:
            return (41, 208, 208)
        case Label.TABLE:
            return (255, 146, 51)
        case Label.TEXT:
            return (255, 238, 51)
        case Label.CAPTION:
            return (233, 222, 187)
        case Label.FOOTNOTE:
            return (255, 205, 243)
        case Label.OTHER:
            return (0, 0, 0)


class DebugPostprocessor(Postprocessor):
    """Saves debug images with annotations."""

    def process(self, documents: Iterator[DocumentReference], outdir: Path) -> Iterator[DocumentReference]:
        for document in documents:
            (outdir / document.path.stem / "debug").mkdir(parents=True, exist_ok=True)
            for item in document.items:
                img = cv2.imread(str(item.path))
                for area in item.layout:
                    color = _label_to_color(area.label)
                    img = cv2.rectangle(
                        img,
                        (int(area.bbox.x0), int(area.bbox.y0)),
                        (int(area.bbox.x1), int(area.bbox.y1)),
                        color,
                        thickness=2,
                    )
                    text_y_pos = area.bbox.y0 - 10 if area.bbox.y0 > 10 else (area.bbox.y1 if area.bbox.y1 < img.shape[0] else area.bbox.y0)
                    img = cv2.putText(
                        img,
                        f"{area.label.name}({area.confidence:.2f})",
                        (int(area.bbox.x0), int(text_y_pos)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        color,
                        3,
                    )

                cv2.imwrite(str(outdir / document.path.stem / "debug" / item.path.name), img)
            yield document
