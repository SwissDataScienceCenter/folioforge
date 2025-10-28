import json
import logging
import os
from pathlib import Path
from typing import Any

import cv2
import google.generativeai as genai
from numpy._typing import NDArray

from folioforge.extraction.protocol import Extractor
from folioforge.models.document import Area, BoundingBox, DocumentEntry, Heading, Image, Table, TableCell
from folioforge.models.labels import Label

PROMPT = """
Analyze this image. Spot every text block, giving its content and precise bounding-box coordinates (normalized 0.0–1.0, origin top-left)
and label.
Valid labels are:
 - CAPTION
 - FOOTNOTE
 - LIST_ITEM
 - PAGE_FOOTER
 - PAGE_HEADER
 - IMAGE
 - SECTION_HEADER
 - TABLE
 - TEXT
 - TITLE
 - OTHER
The response must be a valid JSON array. Each element in the array should be an object representing a single text block, with the following
structure:
{
  "label": "TEXT",
  "boundingBox": {
    "x": 0.123,  // Normalized top-left x-coordinate (0.0 to 1.0, from left edge of the image).
    "y": 0.456,  // Normalized top-left y-coordinate (0.0 to 1.0, from top edge of the image).
    "width": 0.789, // Normalized width of the bounding box (0.0 to 1.0, relative to image width).
    "height": 0.012 // Normalized height of the bounding box (0.0 to 1.0, relative to image height).
  }
  "text": "The extracted text content from the block.",
  "headers": [ // only on label "TABLE"
      {
        "row_span": 1, // how many rows the header spans
        "col_span": 1, // how many columns the header spans
        "start_row": 0, // the row the header is on
        "end_row": 1, // the row the header ends at (the following row)
        "start_col": 0, // the column the header is on
        "end_col": 1, // the column the header ends at (the following column)
        "converted": "The extracted text of the header"
      },
  ],
  "cells": [ // only on label "TABLE"
      {
        "row_span": 1, // how many rows the cell spans
        "col_span": 1, // how many columns the cell spans
        "start_row": 0, // the row the cell is on
        "end_row": 1, // the row the cell ends at (the following row)
        "start_col": 0, // the column the cell is on
        "end_col": 1, // the column the cell ends at (the following column)
        "converted": "The extracted text of the cell"
      },
  ]
}
Ensure all coordinates in "boundingBox" are normalized values between 0.0 and 1.0, relative to the dimensions of their specific image.
The origin (0,0) for x and y is the top-left corner of the image.
If a image has no text, provide an empty array.
The JSON output should be clean, directly parsable, and match the format of the example provided. (example.png and example.json files )
"""


class GeminiExtractor(Extractor):
    def __init__(self, api_key: str = os.getenv("GEMINI_API_KEY", ""), retries: int = 3) -> None:
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        self.example_file_upload = genai.upload_file(path=Path(__file__).parent.parent / "assets" / "example.png")
        self.example_json_string = (Path(__file__).parent.parent / "assets" / "example.json").read_text()
        self.retries = retries

    def extract(self, entry: DocumentEntry) -> DocumentEntry:
        page_upload = genai.upload_file(path=str(entry.path))

        prompt_parts = [
            # First user message: The instruction and the example file
            PROMPT,
            self.example_file_upload,
            # First model response: The perfect JSON output for the example
            self.example_json_string,
            page_upload,
        ]
        retries = self.retries

        while True:
            print("Querying Gemini model with few-shot OCR prompt...")
            response = self.model.generate_content(prompt_parts)
            cleaned_text = self.clean_json_response(response.text)
            try:
                page_blocks = json.loads(cleaned_text)
            except json.JSONDecodeError:
                retries -= 1
                if retries == 0:
                    logging.warning(f"Couldn't get a valid json response from Gemini for page {entry.path.name}")
                    return entry
                continue
            break

        img = cv2.imread(str(entry.path))
        assert img is not None
        entry.layout = [self.convert_block(block, img, entry, chunk_id) for chunk_id, block in enumerate(page_blocks)]
        return entry

    def convert_block(self, block: dict[str, Any], img: NDArray, entry: DocumentEntry, chunk: int) -> Area:
        rows, cols = img.shape[:2]
        # todo: use pydantic
        bbox_json: dict[str, float] = block.get("boundingBox")  # type: ignore
        x = bbox_json["x"] * cols
        y = bbox_json["y"] * rows
        bbox = BoundingBox(x0=x, y0=y, x1=x + bbox_json["width"] * cols, y1=y + bbox_json["height"] * rows)
        label = block.get("label", "Other")
        match label:
            case "TABLE":
                headers = []
                if headers_data := block.get("headers"):
                    headers = [
                        TableCell(
                            bbox=None,
                            row_span=header["row_span"],
                            col_span=header["row_span"],
                            start_row=header["start_row"],
                            end_row=header["end_row"],
                            start_col=header["start_col"],
                            end_col=header["end_col"],
                            converted=header["converted"],
                        )
                        for header in headers_data
                    ]
                cells = []
                if cells_data := block.get("cells"):
                    cells = [
                        TableCell(
                            bbox=None,
                            row_span=cell["row_span"],
                            col_span=cell["row_span"],
                            start_row=cell["start_row"],
                            end_row=cell["end_row"],
                            start_col=cell["start_col"],
                            end_col=cell["end_col"],
                            converted=cell["converted"],
                        )
                        for cell in cells_data
                    ]
                return Table(bbox=bbox, label=Label.TABLE, confidence=1.0, headers=headers, cells=cells, converted=block["text"])
            case "IMAGE":
                img_path = Path(entry.path).parent / f"image_{entry.path.stem}_{chunk}.png"
                cropped = img[int(bbox.y0) : int(bbox.y1), int(bbox.x0) : int(bbox.x1)]
                cv2.imwrite(str(img_path), cropped)
                return Image(bbox=bbox, label=Label.IMAGE, confidence=1.0, converted=None, path=img_path)
            case "TITLE":
                return Heading(level=1, bbox=bbox, label=Label.TITLE, confidence=1.0, converted=block["text"])
            case "SECTION_HEADER":
                return Heading(level=2, bbox=bbox, label=Label.SECTION_HEADER, confidence=1.0, converted=block["text"])
            case _:
                return Area(
                    bbox=bbox,
                    label=Label[label],
                    confidence=1.0,
                    converted=block["text"],
                )

    def clean_json_response(self, text: str) -> str:
        if "```json" in text:
            text = text.split("```json\n", 1)[1]
        if "```" in text:
            text = text.rsplit("\n```", 1)[0]
        return text.strip()
