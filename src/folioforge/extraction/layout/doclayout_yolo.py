from doclayout_yolo import YOLOv10
from huggingface_hub import hf_hub_download

from folioforge.extraction.layout.protocol import LayoutDetector
from folioforge.models.document import Area, BoundingBox, DocumentEntry, Heading, Image, Table
from folioforge.models.labels import Label


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
        for box in boxes:
            bbox = BoundingBox(x0=box["box"]["x1"], y0=box["box"]["y1"], x1=box["box"]["x2"], y1=box["box"]["y2"])
            confidence = box["confidence"]

            area = self.map_label(box["name"], bbox, confidence)
            document.layout.append(area)

        return document

    def map_label(self, label: str, bbox: BoundingBox, confidence: float) -> Area:
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


class DoclayoutYOLOD4LA(DoclayoutYOLODocLayNet):
    repo_id = "juliozhao/DocLayout-YOLO-D4LA-Docsynth300K_pretrained"
    filename = "doclayout_yolo_d4la_imgsz1600_docsynth_pretrain.pt"
    imgsz = 1600

    def map_label(self, label: str, bbox: BoundingBox, confidence: float) -> Area:
        # https://openaccess.thecvf.com/content/ICCV2023/supplemental/Da_Vision_Grid_Transformer_ICCV_2023_supplemental.pdf
        matched_label: Label
        match label:
            case "FigureName":
                matched_label = Label.CAPTION
            case "ListText" | "RegionList" | "Catalog":
                matched_label = Label.LIST_ITEM
            case "PageFooter":
                matched_label = Label.PAGE_FOOTER
            case "PageHeader":
                matched_label = Label.PAGE_HEADER
            case "Figure":
                matched_label = Label.IMAGE
            case "RegionTitle" | "ParaTitle" | "RegionKV":
                matched_label = Label.SECTION_HEADER
            case "Table":
                matched_label = Label.TABLE
            case "OtherText" | "ParaText" | "Number" | "Question" | "Date" | "LetterHead" | "LetterDear" | "LetterSign":
                matched_label = Label.TEXT
            case "DocTitle":
                matched_label = Label.TITLE
            case "Reference":
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


class DoclayoutYOLODocStructBench(DoclayoutYOLODocLayNet):
    repo_id = "juliozhao/DocLayout-YOLO-DocStructBench"
    filename = "doclayout_yolo_docstructbench_imgsz1024.pt"
    imgsz = 1024

    def map_label(self, label: str, bbox: BoundingBox, confidence: float) -> Area:
        # https://arxiv.org/pdf/2410.12628 Appendix A.1
        matched_label: Label
        match label:
            case "FigureCaption" | "TableCaption" | "FormulaCaption":
                matched_label = Label.CAPTION
            case "Figure" | "IsolateFormula":
                matched_label = Label.IMAGE
            case "Table":
                matched_label = Label.TABLE
            case "PlainText":
                matched_label = Label.TEXT
            case "Title":
                matched_label = Label.TITLE
            case "TableFootnote":
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
