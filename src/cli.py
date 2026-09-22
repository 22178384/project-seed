"""Command-line front end for txtstat.

Only two responsibilities: parse args, and print results. All the math lives in
core.py. If you're adding a feature, it probably belongs in core.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .core import analyze_text, top_words

# 0 = everything fine, 1 = at least one file couldn't be read, 2 = bad usage.
EXIT_OK = 0
EXIT_IO_ERROR = 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="txtstat",
        description="Line/word/char stats with a reading-time estimate.",
    )
    p.add_argument(
        "paths",
        nargs="*",
        metavar="FILE",
        help="files to analyze; use '-' for stdin (default if none given)",
    )
    p.add_argument("--json", action="store_true", help="emit JSON instead of text")
    p.add_argument(
        "--top", type=int, default=5, metavar="N",
        help="how many frequent words to show (default: 5, 0 to disable)",
    )
    p.add_argument("--version", action="version", version=f"txtstat {__version__}")
    return p


def read_source(path: str) -> tuple[str, str]:
    """Return (label, text) for one path. '-' means stdin.

    Reading with errors='replace' instead of raising: I'd rather get stats with
    a few U+FFFD replacement chars than have the whole run fail on one bad byte.
    """
    if path == "-":
        return "<stdin>", sys.stdin.read()
    p = Path(path)
    return str(p), p.read_text(encoding="utf-8", errors="replace")


def format_human(stats, top: list[tuple[str, int]]) -> str:
    lines = [
        stats.path,
        f"  lines         {stats.lines}",
        f"  words         {stats.words}",
        f"  chars         {stats.chars}",
        f"  longest line  {stats.longest_line}",
        f"  read time     {stats.reading_minutes} min",
    ]
    if top:
        rendered = " ".join(f"{w}({c})" for w, c in top)
        lines.append(f"  top words     {rendered}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = args.paths or ["-"]
    exit_code = EXIT_OK
    records = []

    for path in paths:
        try:
            label, text = read_source(path)
        except OSError as exc:
            # Don't die on the first missing file; report and keep going.
            print(f"txtstat: {path}: {exc.strerror or exc}", file=sys.stderr)
            exit_code = EXIT_IO_ERROR
            continue

        stats = analyze_text(text, path=label)
        top = top_words(text, args.top)
        records.append({"stats": stats.as_dict(), "top_words": top})

        if not args.json:
            print(format_human(stats, top))

    if args.json:
        print(json.dumps(records, ensure_ascii=False, indent=2))

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
