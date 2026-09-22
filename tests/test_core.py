"""Unit tests for src.core.

These deliberately poke at the empty-input and trailing-newline cases, since
those are where wc-style tools usually disagree with each other.
"""

from __future__ import annotations

import pytest

from src.core import Stats, analyze_text, count_lines, reading_time, top_words


class TestCountLines:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("", 0),                     # empty is zero, not one
            ("a", 1),                    # no trailing newline
            ("a\n", 1),                  # trailing newline doesn't add a line
            ("a\nb", 2),
            ("a\nb\n", 2),
            ("\n", 1),                   # a single blank line
            ("a\n\nb", 3),               # blank line in the middle counts
        ],
    )
    def test_cases(self, text: str, expected: int) -> None:
        assert count_lines(text) == expected


class TestReadingTime:
    def test_one_minute_at_default_wpm(self) -> None:
        assert reading_time(220) == 1.0

    def test_rounds_to_one_decimal(self) -> None:
        # 500 / 220 = 2.2727...
        assert reading_time(500) == 2.3

    def test_zero_words(self) -> None:
        assert reading_time(0) == 0.0

    def test_custom_wpm(self) -> None:
        assert reading_time(300, wpm=300) == 1.0

    def test_non_positive_wpm_raises(self) -> None:
        with pytest.raises(ValueError):
            reading_time(100, wpm=0)
        with pytest.raises(ValueError):
            reading_time(100, wpm=-50)


class TestTopWords:
    def test_basic_frequency(self) -> None:
        result = top_words("the cat the dog the", n=2)
        assert result == [("the", 3), ("cat", 1)]

    def test_case_is_folded(self) -> None:
        assert top_words("Go go GO", n=1) == [("go", 3)]

    def test_ties_break_alphabetically(self) -> None:
        # Both appear once; "apple" must come before "banana" regardless of
        # insertion order.
        assert top_words("banana apple", n=2) == [("apple", 1), ("banana", 1)]

    def test_punctuation_not_part_of_word(self) -> None:
        # "don't" keeps its apostrophe, but the trailing period is dropped.
        result = dict(top_words("don't don't.", n=5))
        assert result == {"don't": 2}

    def test_n_zero_returns_empty(self) -> None:
        assert top_words("anything here", n=0) == []

    def test_n_larger_than_vocab(self) -> None:
        assert len(top_words("one two", n=100)) == 2


class TestAnalyzeText:
    def test_empty_text(self) -> None:
        stats = analyze_text("")
        assert isinstance(stats, Stats)
        assert stats.lines == 0
        assert stats.words == 0
        assert stats.chars == 0
        assert stats.longest_line == 0

    def test_counts_are_consistent(self) -> None:
        text = "hello world\nthis is a test\n"
        stats = analyze_text(text, path="demo.txt")
        assert stats.path == "demo.txt"
        assert stats.lines == 2
        assert stats.words == 6
        assert stats.chars == len(text)
        # "this is a test" (14) is longer than "hello world" (11)
        assert stats.longest_line == len("this is a test")

    def test_longest_line_picks_max(self) -> None:
        text = "short\nthis line is much longer\nmid\n"
        assert analyze_text(text).longest_line == len("this line is much longer")

    def test_as_dict_roundtrip(self) -> None:
        d = analyze_text("hi").as_dict()
        assert set(d) == {
            "path", "lines", "words", "chars", "longest_line", "reading_minutes"
        }
        assert d["words"] == 1
