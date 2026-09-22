"""End-to-end tests for the CLI, run as a subprocess.

I use subprocess rather than calling main() directly so the tests also cover
stdin handling, exit codes, and the actual installed entry point behavior.
Slower (~100ms each) but catches the bugs I actually ship.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# Run as a module so this works whether or not the console script is on PATH.
CMD = [sys.executable, "-m", "src.cli"]

SAMPLE = "the quick brown fox\njumps over the lazy dog\nthe end\n"


def run(args: list[str], stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        CMD + args,
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_version_flag() -> None:
    proc = run(["--version"])
    assert proc.returncode == 0
    assert proc.stdout.startswith("txtstat ")


def test_reads_stdin_with_dash() -> None:
    proc = run(["-"], stdin=SAMPLE)
    assert proc.returncode == 0
    assert "<stdin>" in proc.stdout
    assert "words         14" in proc.stdout  # 4 + 5 + 2 + "the" + ... see note
    assert "lines         3" in proc.stdout


def test_reads_file(tmp_path: Path) -> None:
    f = tmp_path / "sample.txt"
    f.write_text(SAMPLE, encoding="utf-8")
    proc = run([str(f)])
    assert proc.returncode == 0
    assert str(f) in proc.stdout


def test_json_output_is_valid_and_parseable(tmp_path: Path) -> None:
    f = tmp_path / "s.txt"
    f.write_text(SAMPLE, encoding="utf-8")
    proc = run([str(f), "--json"])
    assert proc.returncode == 0
    records = json.loads(proc.stdout)
    assert isinstance(records, list) and len(records) == 1
    rec = records[0]
    assert rec["stats"]["lines"] == 3
    assert rec["top_words"][0][0] == "the"   # "the" appears 3x
    assert rec["top_words"][0][1] == 3


def test_missing_file_exits_1_and_keeps_going(tmp_path: Path) -> None:
    good = tmp_path / "good.txt"
    good.write_text("hello\n", encoding="utf-8")
    proc = run([str(tmp_path / "nope.txt"), str(good)])
    # Missing file is reported but doesn't abort the whole run.
    assert proc.returncode == 1
    assert "nope.txt" in proc.stderr
    assert str(good) in proc.stdout          # the good file still got analyzed
    assert "words         1" in proc.stdout


def test_top_zero_hides_word_list() -> None:
    proc = run(["-", "--top", "0"], stdin=SAMPLE)
    assert proc.returncode == 0
    assert "top words" not in proc.stdout


def test_defaults_to_stdin_when_no_args() -> None:
    proc = run([], stdin="just some words\n")
    assert proc.returncode == 0
    assert "<stdin>" in proc.stdout
