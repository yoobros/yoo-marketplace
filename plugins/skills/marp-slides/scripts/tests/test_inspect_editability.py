"""Contract tests for the dependency-free PPTX editability inspector."""

from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


SCRIPT = (
    Path(__file__).resolve().parents[1] / "inspect_editability.py"
)


NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
}


def make_pptx(path: Path, slide_xml: str, rels_xml: str | None = None) -> None:
    """Create the smallest PPTX-like ZIP package needed by the inspector."""

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as package:
        package.writestr("ppt/slides/slide1.xml", slide_xml)
        if rels_xml is not None:
            package.writestr("ppt/slides/_rels/slide1.xml.rels", rels_xml)


def run_inspector(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def parse_report(result: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(result.stdout)


class InspectEditabilityTests(unittest.TestCase):
    def test_text_and_shape_slide_is_editable(self) -> None:
        slide = f"""<?xml version='1.0' encoding='UTF-8'?>
<p:sld xmlns:p='{NS['p']}' xmlns:a='{NS['a']}'>
  <p:cSld><p:spTree>
    <p:sp><p:nvSpPr/><p:txBody><a:p><a:r><a:t>Editable title</a:t></a:r></a:p></p:txBody></p:sp>
  </p:spTree></p:cSld>
</p:sld>"""

        with TemporaryDirectory() as directory:
            deck = Path(directory) / "editable.pptx"
            make_pptx(deck, slide)
            result = run_inspector(deck, "--require-editable")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = parse_report(result)
        self.assertTrue(report["editable"])
        self.assertEqual(report["failures"], [])
        self.assertEqual(report["totals"]["slides"], 1)
        self.assertEqual(report["totals"]["shapes"], 1)
        self.assertEqual(report["totals"]["text"], 1)
        self.assertFalse(report["slides"][0]["image_only"])

    def test_full_slide_image_only_is_rejected(self) -> None:
        slide = f"""<?xml version='1.0' encoding='UTF-8'?>
<p:sld xmlns:p='{NS['p']}' xmlns:a='{NS['a']}'>
  <p:cSld><p:spTree>
    <p:pic><p:nvPicPr/><p:blipFill/><p:spPr/></p:pic>
  </p:spTree></p:cSld>
</p:sld>"""

        with TemporaryDirectory() as directory:
            deck = Path(directory) / "flattened.pptx"
            make_pptx(deck, slide)
            result = run_inspector(deck, "--require-editable")

        self.assertEqual(result.returncode, 1, result.stderr)
        report = parse_report(result)
        self.assertFalse(report["editable"])
        self.assertEqual(report["slides"][0]["images"], 1)
        self.assertTrue(report["slides"][0]["image_only"])
        self.assertIn("slide1.xml", " ".join(report["failures"]))

    def test_native_table_and_chart_are_counted(self) -> None:
        slide = f"""<?xml version='1.0' encoding='UTF-8'?>
<p:sld xmlns:p='{NS['p']}' xmlns:a='{NS['a']}' xmlns:c='{NS['c']}' xmlns:r='http://schemas.openxmlformats.org/officeDocument/2006/relationships'>
  <p:cSld><p:spTree>
    <p:sp><p:nvSpPr/><p:txBody><a:p><a:r><a:t>Table and chart</a:t></a:r></a:p></p:txBody></p:sp>
    <p:graphicFrame><a:graphic><a:graphicData uri='http://schemas.openxmlformats.org/drawingml/2006/table'>
      <a:tbl><a:tblGrid/><a:tr><a:tc><a:txBody><a:p><a:r><a:t>Cell</a:t></a:r></a:p></a:txBody></a:tc></a:tr></a:tbl>
    </a:graphicData></a:graphic></p:graphicFrame>
    <p:graphicFrame><a:graphic><a:graphicData uri='http://schemas.openxmlformats.org/drawingml/2006/chart'>
      <c:chart r:id='rId1'/>
    </a:graphicData></a:graphic></p:graphicFrame>
    <p:cxnSp><p:nvCxnSpPr/><p:spPr/></p:cxnSp>
  </p:spTree></p:cSld>
</p:sld>"""
        rels = """<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'>
  <Relationship Id='rId1' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart' Target='../charts/chart1.xml'/>
</Relationships>"""

        with TemporaryDirectory() as directory:
            deck = Path(directory) / "native-objects.pptx"
            make_pptx(deck, slide, rels)
            result = run_inspector(deck, "--require-editable")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = parse_report(result)
        self.assertTrue(report["editable"])
        self.assertEqual(report["totals"]["tables"], 1)
        self.assertEqual(report["totals"]["charts"], 1)
        self.assertEqual(report["totals"]["connectors"], 1)
        self.assertEqual(report["totals"]["text"], 2)

    def test_invalid_zip_returns_input_error(self) -> None:
        with TemporaryDirectory() as directory:
            deck = Path(directory) / "not-a-pptx.pptx"
            deck.write_bytes(b"not a zip")
            result = run_inspector(deck)

        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
