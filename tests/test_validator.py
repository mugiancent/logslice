"""Tests for logslice.validator."""
import pytest
from logslice.validator import (
    require_fields,
    require_type,
    require_pattern,
    apply_validations,
    is_valid,
)


class TestRequireFields:
    def test_all_present_returns_empty(self):
        assert require_fields({"a": 1, "b": 2}, ["a", "b"]) == []

    def test_missing_field_returns_error(self):
        errors = require_fields({"a": 1}, ["a", "b"])
        assert len(errors) == 1
        assert errors[0]["field"] == "b"

    def test_empty_required_list(self):
        assert require_fields({}, []) == []

    def test_all_missing(self):
        errors = require_fields({}, ["x", "y"])
        assert len(errors) == 2


class TestRequireType:
    def test_correct_type_returns_empty(self):
        assert require_type({"count": 5}, "count", int) == []

    def test_wrong_type_returns_error(self):
        errors = require_type({"count": "five"}, "count", int)
        assert len(errors) == 1
        assert "expected int" in errors[0]["error"]

    def test_missing_field_returns_empty(self):
        assert require_type({}, "count", int) == []


class TestRequirePattern:
    def test_matching_value_returns_empty(self):
        assert require_pattern({"level": "info"}, "level", r"info|warn|error") == []

    def test_non_matching_value_returns_error(self):
        errors = require_pattern({"level": "debug"}, "level", r"info|warn|error")
        assert len(errors) == 1
        assert "debug" in errors[0]["error"]

    def test_missing_field_returns_empty(self):
        assert require_pattern({}, "level", r"info|warn") == []


class TestApplyValidations:
    def test_no_rules_returns_empty(self):
        assert apply_validations({"a": 1}, []) == []

    def test_collects_errors_from_multiple_rules(self):
        record = {"level": "bad", "count": "x"}
        rules = [
            lambda r: require_fields(r, ["msg"]),
            lambda r: require_type(r, "count", int),
        ]
        errors = apply_validations(record, rules)
        assert len(errors) == 2


class TestIsValid:
    def test_valid_record(self):
        rules = [lambda r: require_fields(r, ["msg"])]
        assert is_valid({"msg": "hello"}, rules) is True

    def test_invalid_record(self):
        rules = [lambda r: require_fields(r, ["msg"])]
        assert is_valid({}, rules) is False
