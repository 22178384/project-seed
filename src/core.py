"""Core logic for txtstat. No printing, no file access — pure functions.

Everything here takes a string and returns data. That makes it testable without
temp files and reusable from a library context. The CLI in cli.py is the only
place that touches the filesystem.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass

# A "word" is letters/digits with an optional internal apostrophe, so "don't"
# counts once and "don't." doesn't pick up the period. Unicode letters are
# included on purpose — I read Chinese docs too.
WORD_RE = re.compile(r"[\w']+", re.UNICODE)

# Median adult reading speed for prose, in words per minute. It's a rough
# number; a technical doc is slower. I'm not going to pretend it's precise.
DEFAULT_WPM = 220


@dataclass(frozen=True)
class Stats:
    """Result of analyzing one text blob."""

    path: str
    lines: int
    words: int
    chars: int
    longest_line: int
    reading_minutes: float

    def as_dict(self) -> dict:
        return asdict(self)


def count_lines(text: str) -> int:
    """Count lines the way `wc -l` does, roughly.

    A trailing newline does not start a new line: "a\\n" is 1 line, "a\\nb" is 2,
    and "" is 0. This differs from `len(text.splitlines())` only in the empty
    case, which is exactly the case people get wrong.
    """
    if not text:
        return 0
    n = text.count("\n")
    if not text.endswith("\n"):
        n += 1
    return n


def reading_time(words: int, wpm: int = DEFAULT_WPM) -> float:
    """Estimate minutes to read `words` words. Rounds to 0.1.

    Guards against wpm <= 0 because I passed 0 once and got a ZeroDivisionError
    from a config file that had `wpm = 0`.
    """
    if wpm <= 0:
        raise ValueError("wpm must be positive")
    return round(words / wpm, 1)


def top_words(text: str, n: int = 5) -> list[tuple[str, int]]:
    """Return the n most common words, lowercased, ties broken alphabetically.

    Counter's default tie order is insertion order, which is unstable across
    runs. Sorting the key as a secondary gives deterministic output — matters
    for the CLI's --json output and for tests.
    """
    if n <= 0:
        return []
    counts = Counter(m.group(0).lower() for m in WORD_RE.finditer(text))
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return ordered[:n]


def analyze_text(text: str, path: str = "<stdin>") -> Stats:
    """Compute all stats for one text blob.

    `path` is only used as a label in the returned Stats; nothing is read from
    disk here.
    """
    words = len(WORD_RE.findall(text))
    lines = count_lines(text)
    longest = max((len(line) for line in text.splitlines()), default=0)
    return Stats(
        path=path,
        lines=lines,
        words=words,
        chars=len(text),
        longest_line=longest,
        reading_minutes=reading_time(words),
    )
