"""Tests for logslice.highlighter."""

import pytest
from logslice.highlighter import (
    _colour,
    highlight_fields,
    highlight_pattern,
    apply_highlights,
    ANSI_CODES,
)


class TestColour:
    def test_known_colour_wraps_text(self):
        result = _colour("hello", "red")
        assert ANSI_CODES["red"] in result
        assert ANSI_CODES["reset"] in result
        assert "hello" in result

    def test_unknown_colour_returns_text_unchanged(self):
        assert _colour("hello", "ultraviolet") == "hello"


class TestHighlightFields:
    def test_colours_specified_field(self):
        record = {"level": "error", "msg": "boom"}
        result = highlight_fields(record, {"level": "red"})
        assert ANSI_CODES["red"] in result["level"]
        assert "error" in result["level"]

    def test_unspecified_field_unchanged(self):
        record = {"level": "error", "msg": "boom"}
        result = highlight_fields(record, {"level": "red"})
        assert result["msg"] == "boom"

    def test_missing_field_ignored(self):
        record = {"msg": "ok"}
        result = highlight_fields(record, {"level": "red"})
        assert "level" not in result

    def test_does_not_mutate_original(self):
        record = {"level": "info"}
        highlight_fields(record, {"level": "green"})
        assert record["level"] == "info"


class TestHighlightPattern:
    def test_wraps_matching_text(self):
        result = highlight_pattern("error occurred", "error")
        assert ANSI_CODES["yellow"] in result
        assert "error" in result

    def test_no_match_returns_original(self):
        result = highlight_pattern("all good", "error")
        assert result == "all good"

    def test_custom_colour(self):
        result = highlight_pattern("warn here", "warn", colour="magenta")
        assert ANSI_CODES["magenta"] in result

    def test_multiple_matches(self):
        result = highlight_pattern("a a a", "a")
        assert result.count(ANSI_CODES["yellow"]) == 3


class TestApplyHighlights:
    def test_applies_field_colours(self):
        records = [{"level": "info", "msg": "hi"}]
        result = apply_highlights(records, field_colours={"level": "cyan"})
        assert ANSI_CODES["cyan"] in result[0]["level"]

    def test_applies_pattern(self):
        records = [{"msg": "error in module"}]
        result = apply_highlights(records, pattern="error")
        assert ANSI_CODES["yellow"] in result[0]["msg"]

    def test_empty_records(self):
        assert apply_highlights([]) == []

    def test_no_options_returns_equivalent_records(self):
        records = [{"a": "1", "b": "2"}]
        result = apply_highlights(records)
        assert result[0]["a"] == "1"
        assert result[0]["b"] == "2"
