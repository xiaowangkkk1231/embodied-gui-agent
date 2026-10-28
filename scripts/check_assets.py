#!/usr/bin/env python3
"""Repository asset validator.

Checks that keep the docs-only repo honest:
  1. every *.svg parses as XML (GitHub renders them, so a broken one is visible to readers);
  2. every *.csv has a consistent number of columns per row;
  3. every relative link in *.md points at a file that exists;
  4. CITATION.cff has the CFF envelope fields GitHub needs.

Exit code 0 = clean, 1 = problems found. No third-party dependencies.
"""

from __future__ import annotations

import csv
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}

errors: list[str] = []
notes: list[str] = []

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def iter_files(pattern: str):
    for path in ROOT.rglob(pattern):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def check_svgs() -> None:
    for path in iter_files("*.svg"):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            errors.append(f"{rel(path)}: invalid XML ({exc})")
            continue
        if root.tag != "{http://www.w3.org/2000/svg}svg":
            errors.append(f"{rel(path)}: root element is <{root.tag}>, expected <svg>")
            continue
        if "viewBox" not in root.attrib:
            notes.append(f"{rel(path)}: missing viewBox (scaling may be odd)")

    notes.append(f"svg checked: {sum(1 for _ in iter_files('*.svg'))}")


def check_csvs() -> None:
    for path in iter_files("*.csv"):
        try:
            with path.open(encoding="utf-8-sig", newline="") as fh:
                rows = [row for row in csv.reader(fh) if any(cell.strip() for cell in row)]
        except OSError as exc:
            errors.append(f"{rel(path)}: cannot read ({exc})")
            continue
        if not rows:
            notes.append(f"{rel(path)}: empty file")
            continue
        width = len(rows[0])
        for lineno, row in enumerate(rows, start=1):
            if len(row) != width:
                errors.append(
                    f"{rel(path)}:{lineno}: {len(row)} columns, header has {width}"
                )


def check_links() -> None:
    for path in iter_files("*.md"):
        text = path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = match.group(1).strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"{rel(path)}: broken relative link -> {target}")


def check_citation() -> None:
    path = ROOT / "CITATION.cff"
    if not path.exists():
        notes.append("CITATION.cff not present (optional)")
        return
    text = path.read_text(encoding="utf-8")
    for field in ("cff-version", "title", "authors", "license", "date-released"):
        if not re.search(rf"^{re.escape(field)}:", text, flags=re.MULTILINE):
            errors.append(f"CITATION.cff: missing required field '{field}'")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def main() -> int:
    check_svgs()
    check_csvs()
    check_links()
    check_citation()

    for note in notes:
        print(f"note: {note}")
    for err in errors:
        print(f"ERROR: {err}", file=sys.stderr)

    if errors:
        print(f"\n{len(errors)} problem(s) found.", file=sys.stderr)
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
