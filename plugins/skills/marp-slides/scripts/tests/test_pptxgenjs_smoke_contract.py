"""Behavioral contract for the cross-platform PptxGenJS smoke deck."""

from __future__ import annotations

import re
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


SKILL_ROOT = Path(__file__).resolve().parents[2]

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}


class PptxGenJSSmokeContractTests(unittest.TestCase):
    def test_npm_smoke_writes_temp_native_deck_with_notes_and_in_bounds_objects(self) -> None:
        result = subprocess.run(
            ["npm", "run", "smoke:pptxgenjs", "--silent"],
            cwd=SKILL_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        output = Path(result.stdout.strip())
        self.assertTrue(output.is_file(), result.stdout)
        self.assertEqual(output.parent.resolve(), Path(tempfile.gettempdir()).resolve())
        self.addCleanup(output.unlink, missing_ok=True)

        with zipfile.ZipFile(output) as package:
            slide = ET.fromstring(package.read("ppt/slides/slide1.xml"))
            presentation = ET.fromstring(package.read("ppt/presentation.xml"))
            notes = [
                name
                for name in package.namelist()
                if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", name)
            ]

            self.assertGreaterEqual(len(slide.findall(".//p:sp", NS)), 1)
            self.assertGreaterEqual(len(slide.findall(".//a:t", NS)), 1)
            self.assertEqual(len(slide.findall(".//a:tbl", NS)), 1)
            self.assertEqual(len(slide.findall(".//c:chart", NS)), 1)
            self.assertEqual(len(notes), 1)
            notes_xml = ET.fromstring(package.read(notes[0]))
            notes_text = " ".join(node.text or "" for node in notes_xml.findall(".//a:t", NS))
            self.assertIn("native text, table, and chart", notes_text)

            slide_size = presentation.find("p:sldSz", NS)
            self.assertIsNotNone(slide_size)
            slide_width = int(slide_size.attrib["cx"])
            slide_height = int(slide_size.attrib["cy"])
            transforms = slide.findall(".//a:xfrm", NS) + slide.findall(".//p:xfrm", NS)
            checked_transforms = 0
            for transform in transforms:
                offset = transform.find("a:off", NS)
                extent = transform.find("a:ext", NS)
                if offset is None or extent is None:
                    continue
                checked_transforms += 1
                x, y = int(offset.attrib["x"]), int(offset.attrib["y"])
                width, height = int(extent.attrib["cx"]), int(extent.attrib["cy"])
                with self.subTest(x=x, y=y, width=width, height=height):
                    self.assertGreaterEqual(x, 0)
                    self.assertGreaterEqual(y, 0)
                    self.assertLessEqual(x + width, slide_width)
                    self.assertLessEqual(y + height, slide_height)
            self.assertGreaterEqual(checked_transforms, 4)


if __name__ == "__main__":
    unittest.main()
