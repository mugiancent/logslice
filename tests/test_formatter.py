"""Tests for logslice.formatter."""

from __future__ import annotations

import pytest

from logslice.formatter import (
    apply_formatters,
    cast_field,
    format_field,
    format_fields,
    lowercase_field,
    uppercase_field,
)


class TestFormatField:
    def test_applies_function(self):
        rec = {"level": "info"}
        result = format_field(rec, "level", str.upper)
        assert result["level"] == "INFO"

    def test_missing_field_unchanged(self):
        rec = {"level": "info"}
        result = format_field(rec, "missing", str.upper)
        assert result == rec

    def test_does_not_mutate_original(self):
        rec = {"level": "info"}
        format_field(rec, "level", str.upper)
        assert rec["level"] == "info"

    def test_other_fields_preserved(self):
        rec = {"level": "info", "msg": "hello"}
        result = format_field(rec, "level", str.upper)
        assert result["msg"] == "hello"


class TestFormatFields:
    def test_applies_multiple(self):
        rec = {"level": "info", "count": "3"}
        result = format_fields(rec, {"level": str.upper, "count": int})
        assert result["level"] == "INFO"
        assert result["count"] == 3

    def test_missing_fields_skipped(self):
        rec = {"level": "info"}
        result = format_fields(rec, {"level": str.upper, "absent": str.lower})
        assert "absent" not in result

    def test_empty_mapping(self):
        rec = {"level": "info"}
        assert format_fields(rec, {}) == rec


class TestApplyFormatters:
    def test_applies_to_all_records(self):
        records = [{"level": "info"}, {"level": "warn"}]
        results = apply_formatters(records, {"level": str.upper})
        assert [r["level"] for r in results] == ["INFO", "WARN"]

    def test_empty_records(self):
        assert apply_formatters([], {"level": str.upper}) == []


class TestUpperLowerField:
    def test_uppercase(self):
        assert uppercase_field({"k": "hello"}, "k")["k"] == "HELLO"

    def test_lowercase(self):
        assert lowercase_field({"k": "HELLO"}, "k")["k"] == "hello"

    def test_non_string_unchanged(self):
        assert uppercase_field({"k": 42}, "k")["k"] == 42


class TestCastField:
    def test_cast_to_int(self):
        result = cast_field({"n": "7"}, "n", int)
        assert result["n"] == 7

    def test_cast_failure_returns_default(self):
        result = cast_field({"n": "bad"}, "n", int, default=-1)
        assert result["n"] == -1

    def test_missing_field_unchanged(self):
        rec = {"x": 1}
        assert cast_field(rec, "missing", int) == rec
