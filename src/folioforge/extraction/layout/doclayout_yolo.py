from folioforge.extraction.layout.protocol import LayoutDetector
from folioforge.models.document import Area, BoundingBox, DocumentEntry, Heading, Table, Image
from doclayout_yolo import YOLOv10
from folioforge.models.labels import Label
from huggingface_hub import hf_hub_download


def map_doclaynet_label(label: str, bbox: BoundingBox, confidence: float) -> Area:
    matched_label: Label
    match label:
        case "Caption":
            matched_label = Label.CAPTION
        case "List-item":
            matched_label = Label.LIST_ITEM
        case "Page-footer":
            matched_label = Label.PAGE_FOOTER
        case "Page-header":
            matched_label = Label.PAGE_HEADER
        case "Picture":
            matched_label = Label.IMAGE
        case "Section-header":
            matched_label = Label.SECTION_HEADER
        case "Table":
            matched_label = Label.TABLE
        case "Text":
            matched_label = Label.TEXT
        case "Title":
            matched_label = Label.TITLE
        case "Footnote":
            matched_label = Label.FOOTNOTE
        case _:
            matched_label = Label.OTHER
    match matched_label:
        case Label.TABLE:
            return Table(bbox=bbox, label=matched_label, confidence=confidence, headers=[], cells=[], converted=None)
        case Label.IMAGE:
            return Image(bbox=bbox, label=matched_label, confidence=confidence, converted=None)
        case Label.TITLE:
            return Heading(level=1, bbox=bbox, label=matched_label, confidence=confidence, converted=None)
        case Label.SECTION_HEADER:
            return Heading(level=2, bbox=bbox, label=matched_label, confidence=confidence, converted=None)
        case _:
            return Area(
                bbox=bbox,
                label=matched_label,
                confidence=confidence,
                converted=None,
            )


class DoclayoutYOLODocLayNet(LayoutDetector):
    repo_id = "juliozhao/DocLayout-YOLO-DocLayNet-Docsynth300K_pretrained"
    filename = "doclayout_yolo_doclaynet_imgsz1120_docsynth_pretrain.pt"
    imgsz = 1120

    def __init__(self):
        filepath = hf_hub_download(self.repo_id, self.filename)
        self.model = YOLOv10(filepath)

    def detect(self, document: DocumentEntry) -> DocumentEntry:
        predictions = self.model.predict(document.path, imgsz=self.imgsz, conf=0.2)
        boxes = predictions[0].summary()
        areas = []
        for box in boxes:
            bbox = BoundingBox(x0=box["box"]["x1"], y0=box["box"]["y1"], x1=box["box"]["x2"], y1=box["box"]["y2"])
            confidence = box["confidence"]

            area = map_doclaynet_label(box["name"], bbox, confidence)
            document.layout.append(area)

        return document


class DoclayoutYOLOD4LA(DoclayoutYOLODocLayNet):
    repo_id = "juliozhao/DocLayout-YOLO-D4LA-Docsynth300K_pretrained"
    filename = "doclayout_yolo_d4la_imgsz1600_docsynth_pretrain.pt"
    imgsz = 1600


class DoclayoutYOLODocStructBench(DoclayoutYOLODocLayNet):
    repo_id = "juliozhao/DocLayout-YOLO-DocStructBench"
    filename = "doclayout_yolo_docstructbench_imgsz1024.pt"
    imgsz = 1024
