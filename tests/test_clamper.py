"""Tests for logslice.clamper."""

import pytest
from logslice.clamper import (
    apply_clamps,
    clamp_all_numeric,
    clamp_field,
    clamp_fields,
    clamp_value,
)


class TestClampValue:
    def test_value_below_lo_is_raised(self):
        assert clamp_value(3, lo=5, hi=10) == 5

    def test_value_above_hi_is_lowered(self):
        assert clamp_value(15, lo=5, hi=10) == 10

    def test_value_within_range_unchanged(self):
        assert clamp_value(7, lo=5, hi=10) == 7

    def test_no_lo_allows_any_low_value(self):
        assert clamp_value(-999, lo=None, hi=100) == -999

    def test_no_hi_allows_any_high_value(self):
        assert clamp_value(999, lo=0, hi=None) == 999

    def test_float_clamped(self):
        assert clamp_value(1.5, lo=2.0, hi=5.0) == 2.0

    def test_non_numeric_string_unchanged(self):
        assert clamp_value("hello", lo=0, hi=10) == "hello"

    def test_bool_unchanged(self):
        # booleans are subclass of int but should not be clamped
        assert clamp_value(True, lo=0, hi=0) is True

    def test_none_unchanged(self):
        assert clamp_value(None, lo=0, hi=10) is None


class TestClampField:
    def test_clamps_existing_field(self):
        rec = {"latency": 200, "status": "ok"}
        result = clamp_field(rec, "latency", lo=0, hi=100)
        assert result["latency"] == 100

    def test_missing_field_returned_unchanged(self):
        rec = {"status": "ok"}
        result = clamp_field(rec, "latency", lo=0, hi=100)
        assert result == rec

    def test_does_not_mutate_original(self):
        rec = {"latency": 200}
        clamp_field(rec, "latency", lo=0, hi=100)
        assert rec["latency"] == 200

    def test_other_fields_preserved(self):
        rec = {"latency": 50, "status": "ok"}
        result = clamp_field(rec, "latency", lo=0, hi=100)
        assert result["status"] == "ok"


class TestClampFields:
    def test_multiple_fields_clamped(self):
        rec = {"a": 5, "b": 15, "c": "text"}
        clamps = {"a": {"lo": 10, "hi": 20}, "b": {"lo": 0, "hi": 10}}
        result = clamp_fields(rec, clamps)
        assert result["a"] == 10
        assert result["b"] == 10
        assert result["c"] == "text"

    def test_empty_clamps_returns_same_values(self):
        rec = {"a": 99}
        assert clamp_fields(rec, {}) == rec


class TestClampAllNumeric:
    def test_all_numeric_fields_clamped(self):
        rec = {"x": -5, "y": 200, "label": "foo"}
        result = clamp_all_numeric(rec, lo=0, hi=100)
        assert result["x"] == 0
        assert result["y"] == 100
        assert result["label"] == "foo"

    def test_no_bounds_leaves_all_unchanged(self):
        rec = {"x": -5, "y": 200}
        result = clamp_all_numeric(rec)
        assert result == rec


class TestApplyClamps:
    def test_applies_to_all_records(self):
        records = [{"v": 0}, {"v": 50}, {"v": 200}]
        clamps = {"v": {"lo": 10, "hi": 100}}
        result = apply_clamps(records, clamps)
        assert [r["v"] for r in result] == [10, 50, 100]

    def test_empty_records_returns_empty(self):
        assert apply_clamps([], {"v": {"lo": 0, "hi": 1}}) == []
