"""Contract tests for the dependency-free PPTX editability inspector."""

from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock
import unittest


SCRIPT = (
    Path(__file__).resolve().parents[1] / "inspect_editability.py"
)
SKILL = Path(__file__).resolve().parents[2] / "SKILL.md"
EDITABLE_REFERENCE = Path(__file__).resolve().parents[2] / "references" / "editable-pptx.md"
PPTXGENJS_REFERENCE = Path(__file__).resolve().parents[2] / "references" / "pptxgenjs.md"
EQUATION_REFERENCE = Path(__file__).resolve().parents[2] / "references" / "editable-equations.md"
EVALS = Path(__file__).resolve().parents[2] / "evals" / "evals.json"
PLUGIN_MANIFEST = Path(__file__).resolve().parents[4] / ".claude-plugin" / "plugin.json"
MARKETPLACE_MANIFEST = Path(__file__).resolve().parents[5] / ".claude-plugin" / "marketplace.json"
PPTXGENJS_SMOKE = Path(__file__).resolve().parents[1] / "smoke_pptxgenjs.mjs"
PPTXGENJS_LOCK = Path(__file__).resolve().parents[2] / "package-lock.json"
PPTXGENJS_PACKAGE = Path(__file__).resolve().parents[2] / "package.json"
PPTXGENJS_WORKFLOW = Path(__file__).resolve().parents[5] / ".github" / "workflows" / "marp-slides-pptxgenjs-smoke.yml"

SPEC = importlib.util.spec_from_file_location("inspect_editability", SCRIPT)
INSPECTOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(INSPECTOR)


NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
}


def make_pptx(path: Path, slide_xml: str, rels_xml: str | None = None) -> None:
    """Create the smallest PPTX-like ZIP package needed by the inspector."""

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as package:
        package.writestr("ppt/slides/slide1.xml", slide_xml)
        if rels_xml is not None:
            package.writestr("ppt/slides/_rels/slide1.xml.rels", rels_xml)


def make_slides_pptx(path: Path, slides: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for name, xml in slides.items():
            package.writestr(f"ppt/slides/{name}", xml)


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
    def test_plugin_metadata_advertises_editable_powerpoint_at_version_1_2_0(self) -> None:
        """Catch stale discovery metadata that still presents flattened PPTX as the feature."""

        plugin = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
        marketplace = json.loads(MARKETPLACE_MANIFEST.read_text(encoding="utf-8"))
        entry = next(item for item in marketplace["plugins"] if item["name"] == "marp-slides")

        self.assertEqual(plugin["version"], "1.2.0")
        self.assertEqual(entry["version"], "1.2.0")
        self.assertIn("editable", plugin["description"].lower())
        self.assertIn("편집", entry["description"])

        for keyword in ["Marp", "LaTeX", "Mermaid", "footnote", "NAVER", "CSS", "Claude Code", "Codex"]:
            with self.subTest(manifest="plugin", keyword=keyword):
                self.assertIn(keyword, plugin["description"])
        for keyword in ["Marp", "LaTeX", "Mermaid", "footnote", "네이버", "CSS", "Claude Code", "Codex"]:
            with self.subTest(manifest="marketplace", keyword=keyword):
                self.assertIn(keyword, entry["description"])

    def test_pptx_evals_cover_editable_defaults_conversion_and_explicit_flattening(self) -> None:
        """Keep all three PPTX routing outcomes measurable in the eval corpus."""

        evals = json.loads(EVALS.read_text(encoding="utf-8"))
        by_name = {case["name"]: case for case in evals}
        required_names = {
            "build-editable-pptx",
            "convert-marp-to-editable-pptx",
            "build-editable-pptx-with-latex",
            "build-flattened-pptx-explicitly",
        }
        self.assertTrue(required_names.issubset(by_name), sorted(by_name))

        editable_contract = [
            "native text",
            "native table/chart",
            "OOXML",
            "inspect_editability.py --require-editable",
            "render every slide",
            "overlap",
            "bounds invasion",
            "clipping",
            "title wrap",
            "severe shrink",
            "excessive whitespace",
            "semantic visual",
        ]
        for name in ["build-editable-pptx", "convert-marp-to-editable-pptx"]:
            case_text = json.dumps(by_name[name], ensure_ascii=False)
            for phrase in editable_contract:
                with self.subTest(eval=name, phrase=phrase):
                    self.assertIn(phrase, case_text)

        flattened = json.dumps(by_name["build-flattened-pptx-explicitly"], ensure_ascii=False)
        for phrase in [
            "marp --pptx",
            "image-based",
            "not individually editable",
            "render every slide",
        ]:
            with self.subTest(eval="build-flattened-pptx-explicitly", phrase=phrase):
                self.assertIn(phrase, flattened)

    def test_skill_defaults_pptx_to_native_editable_objects(self) -> None:
        """Catch a regression to Marp's flattened PPTX as the default route."""

        skill = SKILL.read_text(encoding="utf-8")
        required = [
            "PPTX는 기본적으로 편집 가능한 네이티브 객체",
            "marp --pptx",
            "presentations:Presentations",
            "inspect_editability.py",
            "비편집형",
        ]

        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)

        quick_start = skill.split("## 새 덱을 만드는 최단 경로", 1)[1].split(
            "## 사전 요구사항", 1
        )[0]
        self.assertNotIn("npm run build:pptx", quick_start)

    def test_editable_guidance_enforces_message_density_and_speaker_notes(self) -> None:
        """Keep the audience-facing layer concise without losing source detail."""

        guidance = "\n".join(
            [
                SKILL.read_text(encoding="utf-8"),
                EDITABLE_REFERENCE.read_text(encoding="utf-8"),
            ]
        )
        for phrase in [
            "한 슬라이드에 하나의 메시지",
            "발표용으로 간결",
            "발표자 노트",
            "의도적인 여백",
            "과도한 빈 공간",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, guidance)

    def test_editable_guidance_maps_information_to_semantic_visuals(self) -> None:
        """Prevent decorative dashboards and mismatched chart choices."""

        reference = EDITABLE_REFERENCE.read_text(encoding="utf-8")
        mappings = [
            ("일정", "간트"),
            ("커뮤니케이션", "순차 흐름"),
            ("추세", "선 차트"),
            ("분포", "히스토그램"),
            ("구성", "파이/도넛"),
            ("비교", "막대/표"),
            ("의사결정", "매트릭스/흐름"),
        ]
        for concept, visual in mappings:
            with self.subTest(concept=concept):
                self.assertIn(concept, reference)
                self.assertIn(visual, reference)
        self.assertIn("차트 크기", reference)

    def test_editable_guidance_requires_iterative_full_deck_visual_qa(self) -> None:
        """Make every delivery loop catch layout failures, not just editability."""

        reference = EDITABLE_REFERENCE.read_text(encoding="utf-8")
        for phrase in [
            "모든 슬라이드",
            "겹침",
            "경계 침범",
            "잘림",
            "제목 줄바꿈",
            "심한 축소",
            "과도한 빈 공간",
            "수정 후 재실행",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, reference)

    def test_claude_code_uses_pptxgenjs_as_the_native_editable_engine(self) -> None:
        """Keep Claude Code on a concrete native route instead of vague fallback advice."""

        guidance = "\n".join(
            [
                SKILL.read_text(encoding="utf-8"),
                EDITABLE_REFERENCE.read_text(encoding="utf-8"),
                PPTXGENJS_REFERENCE.read_text(encoding="utf-8"),
            ]
        )
        for phrase in [
            "Claude Code",
            "PptxGenJS",
            "Node.js 18",
            "pptxgenjs@4.0.1",
            "package-lock.json",
            "npm ci",
            "자동 폴백",
            "LibreOffice",
            "발표자 노트",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, guidance)

    def test_codex_and_claude_share_one_editable_output_contract(self) -> None:
        """Keep harness differences limited to tooling, not deliverable quality."""

        reference = EDITABLE_REFERENCE.read_text(encoding="utf-8")
        for phrase in ["Codex와 Claude Code", "도구만 다르고", "산출물 계약", "동일"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, reference)

    def test_pptxgenjs_smoke_is_cross_platform_and_checks_native_ooxml(self) -> None:
        """Require the installability claim to be exercised on all hosted desktop OSes."""

        workflow = PPTXGENJS_WORKFLOW.read_text(encoding="utf-8")
        smoke = PPTXGENJS_SMOKE.read_text(encoding="utf-8")
        for runner in ["macos-latest", "ubuntu-latest", "windows-latest"]:
            with self.subTest(runner=runner):
                self.assertIn(runner, workflow)
        for phrase in ["node-version: 18", "pptxgenjs@4.0.1", "smoke_pptxgenjs.mjs", "inspect_editability.py", "--require-editable"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, workflow)
        for phrase in ["addText", "addChart", "addTable", "addShape", "addNotes", "writeFile"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, smoke)
        self.assertIn("createRequire", smoke)

    def test_pptxgenjs_package_exposes_local_smoke_command(self) -> None:
        """Keep the same native smoke check directly runnable before a PR."""

        package = json.loads(PPTXGENJS_PACKAGE.read_text(encoding="utf-8"))
        self.assertEqual(
            package.get("scripts", {}).get("smoke:pptxgenjs"),
            "node scripts/smoke_pptxgenjs.mjs pptxgenjs-smoke.pptx",
        )

    def test_pptxgenjs_guidance_discloses_current_image_parser_advisories(self) -> None:
        """Do not turn a successful install smoke into a silent supply-chain claim."""

        reference = PPTXGENJS_REFERENCE.read_text(encoding="utf-8")
        workflow = PPTXGENJS_WORKFLOW.read_text(encoding="utf-8")
        for phrase in ["npm audit", "GHSA-w3rx-r6r6-pgpr", "GHSA-5p2g-fcmc-qvqq", "비신뢰"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, reference)
        self.assertIn("npm audit --audit-level=critical", workflow)

    def test_pptxgenjs_lockfile_is_portable_outside_the_corporate_network(self) -> None:
        """Keep public hosted runners from resolving dependencies through a private registry."""

        lockfile = PPTXGENJS_LOCK.read_text(encoding="utf-8")
        self.assertIn("https://registry.npmjs.org/", lockfile)
        self.assertNotIn("artifactory.navercorp.com", lockfile)

    def test_latex_guidance_requires_native_office_math_in_every_runtime(self) -> None:
        """Prevent equations from becoming pictures or plain text in editable PPTX output."""

        guidance = "\n".join(
            [
                SKILL.read_text(encoding="utf-8"),
                EDITABLE_REFERENCE.read_text(encoding="utf-8"),
                EQUATION_REFERENCE.read_text(encoding="utf-8"),
            ]
        )
        for phrase in [
            "Office Math (OMML)",
            "m:oMath",
            "a14:m",
            "PptxGenJS 4.0.1",
            "네이티브 수식 API",
            "SVG/PNG",
            "일반 텍스트",
            "자동 폴백",
            "--require-equations",
            "PowerPoint에서 수식 편집 모드",
            "Codex와 Claude Code",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, guidance)

    def test_html_and_pdf_build_routes_remain_available(self) -> None:
        """Editable PPTX guidance must not regress Marp HTML/PDF behavior."""

        skill = SKILL.read_text(encoding="utf-8")
        for command in [
            '"build": "marp src/slides.md --html',
            '"build:pdf": "marp src/slides.md --html',
            '"build:all": "npm run build && npm run build:pdf"',
            '"build:pptx:flattened": "marp src/slides.md --html',
        ]:
            with self.subTest(command=command):
                self.assertIn(command, skill)

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

    def test_one_picture_with_editable_text_is_not_image_only(self) -> None:
        slide = f"""<p:sld xmlns:p='{NS['p']}' xmlns:a='{NS['a']}'>
  <p:cSld><p:spTree>
    <p:pic><p:nvPicPr/><p:blipFill/><p:spPr/><a:t>Editable caption</a:t></p:pic>
  </p:spTree></p:cSld>
</p:sld>"""
        with TemporaryDirectory() as directory:
            deck = Path(directory) / "picture-and-text.pptx"
            make_pptx(deck, slide)
            result = run_inspector(deck, "--require-editable")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = parse_report(result)
        self.assertTrue(report["editable"])
        self.assertFalse(report["slides"][0]["image_only"])
        self.assertEqual(report["slides"][0]["text"], 1)

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

    def test_native_office_math_is_counted_and_can_be_required(self) -> None:
        slide = f"""<?xml version='1.0' encoding='UTF-8'?>
<p:sld xmlns:p='{NS['p']}' xmlns:a='{NS['a']}' xmlns:m='{NS['m']}' xmlns:a14='http://schemas.microsoft.com/office/drawing/2010/main' xmlns:mc='http://schemas.openxmlformats.org/markup-compatibility/2006'>
  <p:cSld><p:spTree>
    <p:sp><p:nvSpPr/><p:txBody><a:p><a:r><a:t>Bayes rule</a:t></a:r></a:p></p:txBody></p:sp>
    <mc:AlternateContent><mc:Choice Requires='a14'>
      <p:sp><p:nvSpPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a14:m>
        <m:oMathPara><m:oMath><m:f><m:num><m:r><m:t>P(A|B)</m:t></m:r></m:num><m:den><m:r><m:t>P(B)</m:t></m:r></m:den></m:f></m:oMath></m:oMathPara>
      </a14:m></a:p></p:txBody></p:sp>
    </mc:Choice><mc:Fallback><p:sp><p:nvSpPr/><p:txBody><a:p/></p:txBody></p:sp></mc:Fallback></mc:AlternateContent>
  </p:spTree></p:cSld>
</p:sld>"""

        with TemporaryDirectory() as directory:
            deck = Path(directory) / "native-equation.pptx"
            make_pptx(deck, slide)
            result = run_inspector(deck, "--require-editable", "--require-equations", "1")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = parse_report(result)
        self.assertEqual(report["slides"][0]["equations"], 1)
        self.assertEqual(report["totals"]["equations"], 1)

    def test_missing_required_native_equation_fails(self) -> None:
        slide = f"""<p:sld xmlns:p='{NS['p']}' xmlns:a='{NS['a']}'>
  <p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>Not native math</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld>
</p:sld>"""
        with TemporaryDirectory() as directory:
            deck = Path(directory) / "missing-equation.pptx"
            make_pptx(deck, slide)
            result = run_inspector(deck, "--require-equations", "1")

        self.assertEqual(result.returncode, 1, result.stderr)
        report = parse_report(result)
        self.assertEqual(report["totals"]["equations"], 0)
        self.assertIn("expected at least 1", " ".join(report["failures"]))

    def test_negative_required_equation_count_is_rejected(self) -> None:
        result = run_inspector(Path("unused.pptx"), "--require-equations", "-1")
        self.assertEqual(result.returncode, 2)
        self.assertIn("non-negative", result.stderr)

    def test_invalid_zip_returns_input_error(self) -> None:
        with TemporaryDirectory() as directory:
            deck = Path(directory) / "not-a-pptx.pptx"
            deck.write_bytes(b"not a zip")
            result = run_inspector(deck)

        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid", result.stderr.lower())

    def test_runtime_zip_read_error_returns_input_error(self) -> None:
        for error in (RuntimeError("unsupported ZIP"), NotImplementedError("ZIP read unavailable")):
            with self.subTest(error=type(error).__name__), mock.patch.object(
                INSPECTOR.zipfile, "ZipFile", side_effect=error
            ):
                self.assertEqual(INSPECTOR.main(["broken.pptx"]), 2)

    def test_slide_order_and_json_report_are_stable(self) -> None:
        slide = f"""<p:sld xmlns:p='{NS['p']}' xmlns:a='{NS['a']}'>
  <p:cSld><p:spTree><p:sp><p:nvSpPr/><p:txBody><a:p><a:r><a:t>Text</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld>
</p:sld>"""
        with TemporaryDirectory() as directory:
            root = Path(directory)
            deck = root / "ordered.pptx"
            report_path = root / "report.json"
            make_slides_pptx(deck, {"slide10.xml": slide, "slide2.xml": slide, "slide1.xml": slide})
            first = run_inspector(deck, "--json", str(report_path))
            second = run_inspector(deck)

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first.stdout, second.stdout)
            self.assertEqual(json.loads(first.stdout), json.loads(report_path.read_text(encoding="utf-8")))
            self.assertEqual(
                [slide["name"] for slide in json.loads(first.stdout)["slides"]],
                ["ppt/slides/slide1.xml", "ppt/slides/slide2.xml", "ppt/slides/slide10.xml"],
            )


if __name__ == "__main__":
    unittest.main()
