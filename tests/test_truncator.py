import pytest
from logslice.truncator import (
    truncate_field,
    truncate_fields,
    truncate_all_strings,
    apply_truncations,
)


class TestTruncateField:
    def test_short_value_unchanged(self):
        r = {"msg": "hello"}
        assert truncate_field(r, "msg", max_length=10) == {"msg": "hello"}

    def test_long_value_truncated(self):
        r = {"msg": "a" * 20}
        result = truncate_field(r, "msg", max_length=10)
        assert result["msg"] == "a" * 10 + "..."

    def test_custom_suffix(self):
        r = {"msg": "hello world"}
        result = truncate_field(r, "msg", max_length=5, suffix="!")
        assert result["msg"] == "hello!"

    def test_missing_field_ignored(self):
        r = {"level": "info"}
        assert truncate_field(r, "msg", max_length=10) == {"level": "info"}

    def test_non_string_field_unchanged(self):
        r = {"count": 12345678901234567890}
        result = truncate_field(r, "count", max_length=5)
        assert result["count"] == 12345678901234567890

    def test_does_not_mutate_original(self):
        r = {"msg": "a" * 20}
        truncate_field(r, "msg", max_length=5)
        assert r["msg"] == "a" * 20

    def test_exact_length_not_truncated(self):
        r = {"msg": "hello"}
        result = truncate_field(r, "msg", max_length=5)
        assert result["msg"] == "hello"

    def test_empty_string_unchanged(self):
        r = {"msg": ""}
        result = truncate_field(r, "msg", max_length=5)
        assert result["msg"] == ""

    def test_suffix_only_appended_when_truncated(self):
        """Suffix should not appear when the value is within max_length."""
        r = {"msg": "hi"}
        result = truncate_field(r, "msg", max_length=10, suffix="...")
        assert result["msg"] == "hi"


class TestTruncateFields:
    def test_truncates_multiple_fields(self):
        r = {"a": "x" * 20, "b": "y" * 20, "c": "short"}
        result = truncate_fields(r, ["a", "b"], max_length=5)
        assert result["a"] == "x" * 5 + "..."
        assert result["b"] == "y" * 5 + "..."
        assert result["c"] == "short"

    def test_empty_fields_list(self):
        r = {"msg": "a" * 20}
        assert truncate_fields(r, [], max_length=5) == r


class TestTruncateAllStrings:
    def test_truncates_all_long_strings(self):
        r = {"a": "x" * 20, "b": "y" * 20}
        result = truncate_all_strings(r, max_length=5)
        assert result["a"] == "x" * 5 + "..."
        assert result["b"] == "y" * 5 + "..."

    def test_skips_non_strings(self):
        r = {"count": 999, "flag": True}
        result = truncate_all_strings(r, max_length=2)
        assert result == r

    def test_short_strings_unchanged(self):
        r = {"a": "hi", "b": "ok"}
        result = truncate_all_strings(r, max_length=10)
        assert result == r


class TestApplyTruncations:
    def test_applies_to_all_records(self):
        records = [{"msg": "a" * 20}, {"msg": "b" * 20}]
        result = apply_truncations(records, fields=["msg"], max_length=5)
        assert all(r["msg"].endswith("...") for r in result)

    def test_none_fields_truncates_all_strings(self):
        records = [{"a": "x" * 20, "n": 1}]
        result = apply_truncations(records, fields=None, max_length=5)
        assert result[0]["a"] == "x" * 5 + "..."
        assert result[0]["n"] == 1

    def test_empty_records(self):
        assert apply_truncations([], fields=["msg"]) == []
