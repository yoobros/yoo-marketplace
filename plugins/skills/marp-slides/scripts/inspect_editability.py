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
from pathlib import Path
from typing import Iterable
import xml.etree.ElementTree as ET


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
C_NS = "http://schemas.openxmlformats.org/drawingml/2006/chart"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"

TAG_NAMES = {
    "shapes": f"{{{P_NS}}}sp",
    "text": f"{{{A_NS}}}t",
    "tables": f"{{{A_NS}}}tbl",
    "charts": f"{{{C_NS}}}chart",
    "images": f"{{{P_NS}}}pic",
    "connectors": f"{{{P_NS}}}cxnSp",
    "equations": f"{{{M_NS}}}oMath",
}

SLIDE_NAME = re.compile(r"^ppt/slides/slide(\d+)\.xml$")
COUNT_KEYS = ("shapes", "text", "tables", "charts", "images", "connectors", "equations")


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
    return {
        key: sum(1 for element in root.iter() if element.tag == tag)
        for key, tag in TAG_NAMES.items()
    }


def _inspect_slide(package: zipfile.ZipFile, name: str) -> dict[str, object]:
    try:
        root = ET.fromstring(package.read(name))
    except (KeyError, ET.ParseError, UnicodeDecodeError) as exc:
        raise InvalidPptxError(f"could not parse {name}: {exc}") from exc

    counts = _count_tags(root)
    # A single picture with no native content is the characteristic flattened
    # Marp export. Count native text independently as editable content because
    # text can occur in a shape, table, chart, or other OOXML object. The
    # explicit p:pic == 1 rule avoids rejecting slides with multiple images.
    editable_count = sum(
        counts[key] for key in ("shapes", "text", "tables", "charts", "connectors", "equations")
    )
    image_only = counts["images"] == 1 and editable_count == 0
    return {"name": name, **counts, "image_only": image_only}


def inspect_pptx(path: Path) -> dict[str, object]:
    """Return a deterministic editability report for *path*."""

    try:
        with zipfile.ZipFile(path) as package:
            if package.testzip() is not None:
                raise InvalidPptxError("PPTX ZIP contains a corrupt entry")
            slides = [_inspect_slide(package, name) for name in _slide_names(package)]
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
        f"{slide['name']} is image-only (one full-slide picture and no editable objects)"
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
