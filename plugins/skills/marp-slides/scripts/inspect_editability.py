#!/usr/bin/env python3
"""Inspect the editable object mix in a PowerPoint OOXML package.

The inspector intentionally uses only Python's standard library so it can run
in a slide project without installing a PPTX dependency.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Iterable
import xml.etree.ElementTree as ET


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
C_NS = "http://schemas.openxmlformats.org/drawingml/2006/chart"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
A14_NS = "http://schemas.microsoft.com/office/drawing/2010/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

TAG_NAMES = {
    "shapes": f"{{{P_NS}}}sp",
    "text": f"{{{A_NS}}}t",
    "tables": f"{{{A_NS}}}tbl",
    "charts": f"{{{C_NS}}}chart",
    "images": f"{{{P_NS}}}pic",
    "connectors": f"{{{P_NS}}}cxnSp",
}

SLIDE_NAME = re.compile(r"^ppt/slides/slide(\d+)\.xml$")
COUNT_KEYS = ("shapes", "text", "tables", "charts", "images", "connectors", "equations")
CORE_PARTS = {
    "[Content_Types].xml",
    "_rels/.rels",
    "ppt/presentation.xml",
    "ppt/_rels/presentation.xml.rels",
}


class InvalidPptxError(ValueError):
    """Raised when the input is not a readable PPTX slide package."""


def _nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("COUNT must be non-negative")
    return parsed


def _slide_sort_key(name: str) -> tuple[int, str]:
    match = SLIDE_NAME.match(name)
    return (int(match.group(1)), name) if match else (sys.maxsize, name)


def _slide_names(package: zipfile.ZipFile) -> list[str]:
    names = [name for name in package.namelist() if SLIDE_NAME.match(name)]
    if not names:
        raise InvalidPptxError("PPTX package has no ppt/slides/slide*.xml entries")
    return sorted(names, key=_slide_sort_key)


def _count_tags(root: ET.Element) -> dict[str, int]:
    counts = {
        key: sum(1 for element in root.iter() if element.tag == tag)
        for key, tag in TAG_NAMES.items()
    }
    equation_tag = f"{{{M_NS}}}oMath"
    math_wrapper_tag = f"{{{A14_NS}}}m"
    counts["equations"] = sum(
        1
        for wrapper in root.iter(math_wrapper_tag)
        for element in wrapper.iter(equation_tag)
    )
    return counts


def _read_xml(package: zipfile.ZipFile, name: str) -> ET.Element:
    try:
        return ET.fromstring(package.read(name))
    except (KeyError, ET.ParseError, UnicodeDecodeError) as exc:
        raise InvalidPptxError(f"could not parse {name}: {exc}") from exc


def _presentation_size(package: zipfile.ZipFile) -> tuple[int, int]:
    root = _read_xml(package, "ppt/presentation.xml")
    size = root.find(f"{{{P_NS}}}sldSz")
    try:
        width = int(size.attrib["cx"])
        height = int(size.attrib["cy"])
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise InvalidPptxError("ppt/presentation.xml has no valid p:sldSz") from exc
    if width <= 0 or height <= 0:
        raise InvalidPptxError("ppt/presentation.xml has invalid slide dimensions")
    return width, height


def _full_slide_image_count(root: ET.Element, slide_size: tuple[int, int]) -> int:
    width, height = slide_size
    count = 0
    for picture in root.iter(f"{{{P_NS}}}pic"):
        transform = picture.find(f".//{{{A_NS}}}xfrm")
        offset = transform.find(f"{{{A_NS}}}off") if transform is not None else None
        extent = transform.find(f"{{{A_NS}}}ext") if transform is not None else None
        try:
            x, y = int(offset.attrib["x"]), int(offset.attrib["y"])
            image_width, image_height = int(extent.attrib["cx"]), int(extent.attrib["cy"])
        except (AttributeError, KeyError, TypeError, ValueError):
            continue
        if (
            x <= width * 0.05
            and y <= height * 0.05
            and x + image_width >= width * 0.95
            and y + image_height >= height * 0.95
        ):
            count += 1
    return count


def _meaningful_shape_count(root: ET.Element) -> int:
    return sum(
        1
        for shape in root.iter(f"{{{P_NS}}}sp")
        if shape.find(f".//{{{A_NS}}}t") is not None
        or shape.find(f".//{{{A_NS}}}prstGeom") is not None
        or shape.find(f".//{{{A_NS}}}custGeom") is not None
    )


def _slide_rels_name(slide_name: str) -> str:
    path = PurePosixPath(slide_name)
    return str(path.parent / "_rels" / f"{path.name}.rels")


def _validate_charts(package: zipfile.ZipFile, slide_name: str, root: ET.Element) -> None:
    charts = list(root.iter(f"{{{C_NS}}}chart"))
    if not charts:
        return
    rels_name = _slide_rels_name(slide_name)
    rels_root = _read_xml(package, rels_name)
    relationships = {
        relationship.attrib.get("Id"): relationship
        for relationship in rels_root.iter(f"{{{PKG_REL_NS}}}Relationship")
    }
    base = PurePosixPath(slide_name).parent
    for chart in charts:
        relationship_id = chart.attrib.get(f"{{{R_NS}}}id")
        relationship = relationships.get(relationship_id)
        if relationship is None or not relationship.attrib.get("Type", "").endswith("/chart"):
            raise InvalidPptxError(f"{slide_name} has an unresolved chart relationship")
        target = relationship.attrib.get("Target")
        if not target:
            raise InvalidPptxError(f"{slide_name} has a chart relationship without a target")
        target_path = target if target.startswith("/") else str(PurePosixPath(base, target))
        normalized_parts: list[str] = []
        for part in PurePosixPath(target_path).parts:
            if part == "..":
                if normalized_parts:
                    normalized_parts.pop()
            elif part not in ("", ".", "/"):
                normalized_parts.append(part)
        normalized_target = "/".join(normalized_parts)
        if normalized_target not in package.namelist():
            raise InvalidPptxError(
                f"{slide_name} chart relationship targets missing part {normalized_target}"
            )


def _inspect_slide(
    package: zipfile.ZipFile, name: str, slide_size: tuple[int, int]
) -> dict[str, object]:
    root = _read_xml(package, name)
    _validate_charts(package, name, root)
    counts = _count_tags(root)
    full_slide_images = _full_slide_image_count(root, slide_size)
    meaningful_shapes = _meaningful_shape_count(root)
    semantic_native_count = sum(
        counts[key] for key in ("text", "tables", "charts", "connectors", "equations")
    ) + meaningful_shapes
    image_only = counts["images"] > 0 and semantic_native_count == 0
    flattened = full_slide_images > 0 and semantic_native_count == 0
    return {
        "name": name,
        **counts,
        "full_slide_images": full_slide_images,
        "image_only": image_only or flattened,
    }


def inspect_pptx(path: Path) -> dict[str, object]:
    """Return a deterministic editability report for *path*."""

    try:
        with zipfile.ZipFile(path) as package:
            if package.testzip() is not None:
                raise InvalidPptxError("PPTX ZIP contains a corrupt entry")
            missing_core = sorted(CORE_PARTS.difference(package.namelist()))
            if missing_core:
                raise InvalidPptxError(
                    f"PPTX package is missing core parts: {', '.join(missing_core)}"
                )
            slide_size = _presentation_size(package)
            slides = [
                _inspect_slide(package, name, slide_size) for name in _slide_names(package)
            ]
    except (
        OSError,
        EOFError,
        RuntimeError,
        NotImplementedError,
        zipfile.BadZipFile,
    ) as exc:
        raise InvalidPptxError(f"invalid PPTX ZIP: {exc}") from exc

    totals: dict[str, int] = {key: sum(int(slide[key]) for slide in slides) for key in COUNT_KEYS}
    totals = {"slides": len(slides), **totals}
    failures = [
        f"{slide['name']} is image-only (pictures and no meaningful editable objects)"
        for slide in slides
        if slide["image_only"]
    ]
    if totals["text"] == 0:
        failures.insert(0, "deck has no editable text objects")

    return {
        "slides": slides,
        "totals": totals,
        "editable": totals["text"] > 0 and not any(slide["image_only"] for slide in slides),
        "failures": failures,
    }


def _write_report(report: dict[str, object], path: Path | None) -> None:
    encoded = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path is not None:
        try:
            path.write_text(encoded, encoding="utf-8")
        except OSError as exc:
            raise InvalidPptxError(f"could not write JSON report {path}: {exc}") from exc
    sys.stdout.write(encoded)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", type=Path, help="PPTX file to inspect")
    parser.add_argument("--json", dest="json_path", type=Path, help="also write the report here")
    parser.add_argument(
        "--require-editable",
        action="store_true",
        help="return exit code 1 when the editability contract is not met",
    )
    parser.add_argument(
        "--require-equations",
        type=_nonnegative_int,
        metavar="COUNT",
        help="return exit code 1 unless at least COUNT native Office Math objects exist",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = inspect_pptx(args.deck)
        equations_missing = (
            args.require_equations is not None
            and int(report["totals"]["equations"]) < args.require_equations
        )
        if equations_missing:
            report["failures"].append(
                f"deck has {report['totals']['equations']} native equations; "
                f"expected at least {args.require_equations}"
            )
        _write_report(report, args.json_path)
    except InvalidPptxError as exc:
        print(f"invalid PPTX input: {exc}", file=sys.stderr)
        return 2

    editable_missing = args.require_editable and not report["editable"]
    return 1 if editable_missing or equations_missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
