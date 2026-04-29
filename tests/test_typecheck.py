"""Tests for logslice.typecheck."""

import pytest

from logslice.typecheck import (
    check_field_type,
    check_fields_types,
    filter_by_type,
    partition_by_type,
    type_errors,
)


class TestCheckFieldType:
    def test_correct_type_returns_true(self):
        assert check_field_type({"age": 42}, "age", int) is True

    def test_wrong_type_returns_false(self):
        assert check_field_type({"age": "42"}, "age", int) is False

    def test_missing_field_returns_false(self):
        assert check_field_type({}, "age", int) is False

    def test_string_type_name_resolved(self):
        assert check_field_type({"name": "alice"}, "name", "str") is True

    def test_unknown_type_name_raises(self):
        with pytest.raises(ValueError, match="Unknown type name"):
            check_field_type({"x": 1}, "x", "uuid")

    def test_bool_is_not_int(self):
        # bool is a subclass of int in Python, so this should pass
        assert check_field_type({"flag": True}, "flag", bool) is True


class TestCheckFieldsTypes:
    def test_all_pass(self):
        record = {"a": 1, "b": "hello"}
        result = check_fields_types(record, {"a": int, "b": str})
        assert result == {"a": True, "b": True}

    def test_partial_fail(self):
        record = {"a": 1, "b": 99}
        result = check_fields_types(record, {"a": int, "b": str})
        assert result == {"a": True, "b": False}

    def test_empty_spec_returns_empty(self):
        assert check_fields_types({"a": 1}, {}) == {}


class TestFilterByType:
    def test_keeps_matching_records(self):
        records = [{"v": 1}, {"v": "x"}, {"v": 2}]
        result = list(filter_by_type(records, "v", int))
        assert result == [{"v": 1}, {"v": 2}]

    def test_missing_field_excluded(self):
        records = [{"v": 1}, {"other": 2}]
        result = list(filter_by_type(records, "v", int))
        assert result == [{"v": 1}]

    def test_empty_input_yields_nothing(self):
        assert list(filter_by_type([], "v", int)) == []

    def test_string_type_name(self):
        records = [{"s": "hello"}, {"s": 123}]
        result = list(filter_by_type(records, "s", "str"))
        assert result == [{"s": "hello"}]


class TestPartitionByType:
    def test_splits_correctly(self):
        records = [{"x": 1}, {"x": "a"}, {"x": 2}]
        passing, failing = partition_by_type(records, "x", int)
        assert passing == [{"x": 1}, {"x": 2}]
        assert failing == [{"x": "a"}]

    def test_all_pass(self):
        records = [{"x": 1}, {"x": 2}]
        passing, failing = partition_by_type(records, "x", int)
        assert len(passing) == 2
        assert failing == []

    def test_all_fail(self):
        records = [{"x": "a"}, {"x": "b"}]
        passing, failing = partition_by_type(records, "x", int)
        assert passing == []
        assert len(failing) == 2


class TestTypeErrors:
    def test_no_errors_when_valid(self):
        record = {"age": 30, "name": "bob"}
        assert type_errors(record, {"age": int, "name": str}) == []

    def test_missing_field_reported(self):
        errs = type_errors({}, {"age": int})
        assert len(errs) == 1
        assert "missing" in errs[0]

    def test_wrong_type_reported(self):
        errs = type_errors({"age": "old"}, {"age": int})
        assert len(errs) == 1
        assert "expected int" in errs[0]
        assert "got str" in errs[0]

    def test_multiple_errors(self):
        record = {"a": "x"}
        errs = type_errors(record, {"a": int, "b": str})
        assert len(errs) == 2
