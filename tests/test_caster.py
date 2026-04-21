"""Tests for logslice.caster."""

from __future__ import annotations

import pytest

from logslice.caster import (
    apply_casts,
    cast_field,
    cast_fields,
    safe_float,
    safe_int,
)


class TestCastField:
    def test_casts_string_to_int(self):
        rec = {"count": "42", "msg": "hello"}
        result = cast_field(rec, "count", int)
        assert result["count"] == 42
        assert isinstance(result["count"], int)

    def test_casts_string_to_float(self):
        rec = {"latency": "3.14"}
        result = cast_field(rec, "latency", float)
        assert result["latency"] == pytest.approx(3.14)

    def test_missing_field_returns_unchanged(self):
        rec = {"msg": "hello"}
        result = cast_field(rec, "count", int)
        assert result == rec

    def test_does_not_mutate_original(self):
        rec = {"count": "7"}
        cast_field(rec, "count", int)
        assert rec["count"] == "7"

    def test_failed_cast_preserves_original_value(self):
        rec = {"count": "abc"}
        result = cast_field(rec, "count", int)
        assert result["count"] == "abc"

    def test_failed_cast_uses_default_when_provided(self):
        rec = {"count": "abc"}
        result = cast_field(rec, "count", int, default=-1)
        assert result["count"] == -1

    def test_other_fields_preserved(self):
        rec = {"count": "5", "level": "info"}
        result = cast_field(rec, "count", int)
        assert result["level"] == "info"


class TestCastFields:
    def test_applies_multiple_casts(self):
        rec = {"count": "3", "latency": "1.5", "msg": "ok"}
        result = cast_fields(rec, {"count": int, "latency": float})
        assert result["count"] == 3
        assert result["latency"] == pytest.approx(1.5)
        assert result["msg"] == "ok"

    def test_empty_cast_map_returns_copy(self):
        rec = {"a": "1"}
        result = cast_fields(rec, {})
        assert result == rec
        assert result is not rec


class TestApplyCasts:
    def test_applies_to_all_records(self):
        records = [{"n": "1"}, {"n": "2"}, {"n": "3"}]
        results = apply_casts(records, {"n": int})
        assert [r["n"] for r in results] == [1, 2, 3]

    def test_empty_records_returns_empty(self):
        assert apply_casts([], {"n": int}) == []


class TestSafeConversions:
    def test_safe_int_valid(self):
        assert safe_int("10") == 10

    def test_safe_int_invalid_returns_default(self):
        assert safe_int("bad", default=-1) == -1

    def test_safe_float_valid(self):
        assert safe_float("2.5") == pytest.approx(2.5)

    def test_safe_float_invalid_returns_default(self):
        assert safe_float("bad", default=0.0) == 0.0
