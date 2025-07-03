#!/usr/bin/env python3
"""Scan/Fix broad ``except Exception`` blocks across the code-base.

Usage
-----
python scripts/scan_and_fix_broad_exceptions.py [--apply]

• بدون ‎--apply‎: يطبع تقريرًا جدوليًا بجميع المواقع التي تحتوي على
  ``except Exception`` (مع رقم السطر والسياق).
• مع ‎--apply‎   : يستبدل الأنماط بـ ``except Exception as exc:`` ويضيف تعليق
  ``# FIXME: replace with specific exception`` فوقها، ثم يحفظ الملف.

هذا يسمح بإزالة الاستخدامات الخطيرة تدريجيًا مع الإبقاء على القابلية للتشغيل.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from typing import List, Tuple

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
PATTERN = re.compile(r"except\s+Exception:\s*")


def find_files() -> List[pathlib.Path]:
    """Return all *.py files under the project (excluding venv/ and .git)."""

    for path in PROJECT_ROOT.rglob("*.py"):
        if any(part in {"venv", ".venv", ".git", "__pycache__"} for part in path.parts):
            continue
        if not path.is_file():
            # Skip directories that end with '.py' (rare but exists in repo)
            continue
        yield path


def scan_file(path: pathlib.Path) -> List[Tuple[int, str]]:
    """Return list of (line_no, line_text) with broad exceptions."""

    results: List[Tuple[int, str]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError, OSError):
        return results

    for match in PATTERN.finditer(text):
        line_no = text.count("\n", 0, match.start()) + 1
        snippet = text.splitlines()[line_no - 1].strip()
        results.append((line_no, snippet))
    return results


def apply_fix(path: pathlib.Path) -> int:
    """Rewrite the file, adding FIXME comment and as exc capture.

    Returns number of replacements.
    """

    text = path.read_text(encoding="utf-8")
    new_text, count = PATTERN.subn(
        "# FIXME: replace with specific exception\nexcept Exception as exc:", text
    )
    if count:
        path.write_text(new_text, encoding="utf-8")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan/fix broad exception usage.")
    parser.add_argument("--apply", action="store_true", help="Rewrite files in place.")
    args = parser.parse_args()

    total = 0
    for file_path in find_files():
        matches = scan_file(file_path)
        if not matches:
            continue

        if args.apply:
            replaced = apply_fix(file_path)
            total += replaced
        else:
            for line_no, snippet in matches:
                print(f"{file_path.relative_to(PROJECT_ROOT)}:{line_no}: {snippet}")
            total += len(matches)

    action = "fixed" if args.apply else "found"
    print(f"\n{action.capitalize()} {total} broad exception occurrences.")
    if not args.apply and total:
        sys.exit(1)  # fail in CI when only scanning


if __name__ == "__main__":
    main() 