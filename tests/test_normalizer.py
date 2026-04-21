"""Tests for logslice.normalizer."""

import pytest

from logslice.normalizer import (
    apply_normalizations,
    normalize_bool,
    normalize_field,
    normalize_fields,
    normalize_none,
    strip_whitespace,
)


class TestNormalizeField:
    def test_applies_function(self):
        record = {"msg": "  hello  "}
        result = normalize_field(record, "msg", strip_whitespace)
        assert result["msg"] == "hello"

    def test_missing_field_unchanged(self):
        record = {"level": "info"}
        result = normalize_field(record, "msg", strip_whitespace)
        assert result == {"level": "info"}

    def test_does_not_mutate_original(self):
        record = {"msg": "  hi  "}
        normalize_field(record, "msg", strip_whitespace)
        assert record["msg"] == "  hi  "

    def test_other_fields_preserved(self):
        record = {"msg": "  hi  ", "level": "debug"}
        result = normalize_field(record, "msg", strip_whitespace)
        assert result["level"] == "debug"


class TestNormalizeFields:
    def test_applies_multiple_normalizers(self):
        record = {"msg": "  hello  ", "flag": "yes"}
        result = normalize_fields(record, {"msg": strip_whitespace, "flag": normalize_bool})
        assert result["msg"] == "hello"
        assert result["flag"] is True

    def test_missing_fields_skipped(self):
        record = {"level": "info"}
        result = normalize_fields(record, {"msg": strip_whitespace})
        assert result == {"level": "info"}


class TestStripWhitespace:
    def test_strips_string(self):
        assert strip_whitespace("  hi  ") == "hi"

    def test_non_string_unchanged(self):
        assert strip_whitespace(42) == 42

    def test_empty_string(self):
        assert strip_whitespace("   ") == ""


class TestNormalizeBool:
    @pytest.mark.parametrize("value", ["true", "True", "TRUE", "yes", "1", "on"])
    def test_truthy_strings(self, value):
        assert normalize_bool(value) is True

    @pytest.mark.parametrize("value", ["false", "False", "FALSE", "no", "0", "off"])
    def test_falsy_strings(self, value):
        assert normalize_bool(value) is False

    def test_bool_passthrough(self):
        assert normalize_bool(True) is True
        assert normalize_bool(False) is False

    def test_unknown_string_unchanged(self):
        assert normalize_bool("maybe") == "maybe"


class TestNormalizeNone:
    def test_empty_string_becomes_none(self):
        assert normalize_none("") is None

    def test_null_string_becomes_none(self):
        assert normalize_none("null") is None

    def test_dash_becomes_none(self):
        assert normalize_none("-") is None

    def test_non_sentinel_unchanged(self):
        assert normalize_none("hello") == "hello"

    def test_custom_sentinels(self):
        assert normalize_none("N/A", none_strings=["N/A"]) is None

    def test_non_string_unchanged(self):
        assert normalize_none(0) == 0


class TestApplyNormalizations:
    def test_applies_to_all_records(self):
        records = [{"msg": "  a  "}, {"msg": "  b  "}]
        result = apply_normalizations(records, {"msg": strip_whitespace})
        assert [r["msg"] for r in result] == ["a", "b"]

    def test_empty_records(self):
        assert apply_normalizations([], {"msg": strip_whitespace}) == []

    def test_does_not_mutate_originals(self):
        records = [{"msg": "  hi  "}]
        apply_normalizations(records, {"msg": strip_whitespace})
        assert records[0]["msg"] == "  hi  "
