"""Tests for logslice.coercer."""
import pytest
from logslice.coercer import (
    coerce_field,
    coerce_to_int,
    coerce_to_float,
    coerce_to_str,
    coerce_to_bool,
    apply_coercions,
)


class TestCoerceField:
    def test_applies_function(self):
        rec = {"x": "42"}
        assert coerce_field(rec, "x", int)["x"] == 42

    def test_missing_field_returns_unchanged(self):
        rec = {"a": 1}
        assert coerce_field(rec, "z", int) == {"a": 1}

    def test_does_not_mutate_original(self):
        rec = {"x": "3"}
        coerce_field(rec, "x", int)
        assert rec["x"] == "3"

    def test_coercion_failure_uses_default(self):
        rec = {"x": "bad"}
        result = coerce_field(rec, "x", int, default=0)
        assert result["x"] == 0

    def test_coercion_failure_no_default_keeps_original(self):
        rec = {"x": "bad"}
        result = coerce_field(rec, "x", int)
        assert result["x"] == "bad"


class TestCoerceToInt:
    def test_string_number(self):
        assert coerce_to_int({"n": "7"}, "n")["n"] == 7

    def test_float_to_int(self):
        assert coerce_to_int({"n": 3.9}, "n")["n"] == 3

    def test_invalid_with_default(self):
        assert coerce_to_int({"n": "abc"}, "n", default=-1)["n"] == -1


class TestCoerceToFloat:
    def test_string_float(self):
        result = coerce_to_float({"v": "1.5"}, "v")
        assert result["v"] == pytest.approx(1.5)

    def test_int_to_float(self):
        result = coerce_to_float({"v": 2}, "v")
        assert isinstance(result["v"], float)


class TestCoerceToStr:
    def test_int_becomes_string(self):
        assert coerce_to_str({"k": 99}, "k")["k"] == "99"

    def test_none_becomes_string(self):
        assert coerce_to_str({"k": None}, "k")["k"] == "None"


class TestCoerceToBool:
    def test_true_string(self):
        assert coerce_to_bool({"b": "true"}, "b")["b"] is True

    def test_false_string(self):
        assert coerce_to_bool({"b": "false"}, "b")["b"] is False

    def test_yes_string(self):
        assert coerce_to_bool({"b": "YES"}, "b")["b"] is True

    def test_integer_one(self):
        assert coerce_to_bool({"b": 1}, "b")["b"] is True

    def test_already_bool(self):
        assert coerce_to_bool({"b": False}, "b")["b"] is False

    def test_invalid_uses_default(self):
        assert coerce_to_bool({"b": "maybe"}, "b", default=False)["b"] is False


class TestApplyCoercions:
    def test_applies_multiple_specs(self):
        records = [{"a": "1", "b": "3.14", "c": "yes"}]
        specs = [
            {"field": "a", "type": "int"},
            {"field": "b", "type": "float"},
            {"field": "c", "type": "bool"},
        ]
        result = apply_coercions(records, specs)
        assert result[0]["a"] == 1
        assert result[0]["b"] == pytest.approx(3.14)
        assert result[0]["c"] is True

    def test_unknown_type_skipped(self):
        records = [{"x": "hello"}]
        specs = [{"field": "x", "type": "datetime"}]
        result = apply_coercions(records, specs)
        assert result[0]["x"] == "hello"

    def test_empty_records(self):
        assert apply_coercions([], [{"field": "a", "type": "int"}]) == []

    def test_empty_specs(self):
        records = [{"a": "1"}]
        assert apply_coercions(records, []) == [{"a": "1"}]
