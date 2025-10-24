from pathlib import Path

import cv2
import numpy as np

from folioforge.models.document import DocumentReference
from folioforge.preprocessor.protocol import Preprocessor


class AutoBrightness(Preprocessor):
    """Automatically adjust brightness for images with total brighness below min_brightness."""

    def __init__(self, min_brightness: float = 0.66) -> None:
        self.min_brightness = min_brightness

    def process(self, document: DocumentReference, outdir: Path) -> DocumentReference | None:
        for entry in document.items:
            img = cv2.imread(str(entry.path))
            cols, rows = img.shape[:2]
            brightness = np.sum(img) / (255 * cols * rows)
            ratio = brightness / self.min_brightness
            if ratio >= 1:
                continue
            img = cv2.convertScaleAbs(img, alpha=1 / ratio, beta=0)
            cv2.imwrite(str(entry.path), img)
        return document


class Grayscale(Preprocessor):
    """Turn image into grayscale."""

    def process(self, document: DocumentReference, outdir: Path) -> DocumentReference | None:
        for entry in document.items:
            img = cv2.imread(str(entry.path))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(str(entry.path), img)
        return document


class Threshold(Preprocessor):
    """Turn image into black and white using Otsu binarization or with a fixed threshold."""

    def __init__(self, threshold: int | None = 128) -> None:
        self.threshold = threshold

    def process(self, document: DocumentReference, outdir: Path) -> DocumentReference | None:
        for entry in document.items:
            img = cv2.imread(str(entry.path), cv2.IMREAD_GRAYSCALE)
            if self.threshold is None:
                img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            else:
                img = cv2.threshold(img, self.threshold, 255, cv2.THRESH_BINARY)[1]
            cv2.imwrite(str(entry.path), img)
        return document
