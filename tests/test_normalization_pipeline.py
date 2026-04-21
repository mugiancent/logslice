"""Tests for logslice.normalization_pipeline."""

import pytest

from logslice.normalization_pipeline import build_normalizer_map, normalize_records


class TestBuildNormalizerMap:
    def test_builtin_strip(self):
        nm = build_normalizer_map({"msg": "strip"})
        assert nm["msg"]("  hi  ") == "hi"

    def test_builtin_bool(self):
        nm = build_normalizer_map({"active": "bool"})
        assert nm["active"]("yes") is True

    def test_builtin_none(self):
        nm = build_normalizer_map({"val": "none"})
        assert nm["val"]("") is None

    def test_callable_passthrough(self):
        fn = str.upper
        nm = build_normalizer_map({"level": fn})
        assert nm["level"] is fn

    def test_unknown_name_raises(self):
        with pytest.raises(ValueError, match="Unknown normalizer"):
            build_normalizer_map({"field": "nonexistent"})

    def test_invalid_type_raises(self):
        with pytest.raises(TypeError):
            build_normalizer_map({"field": 42})  # type: ignore[arg-type]


class TestNormalizeRecords:
    def test_strip_applied(self):
        records = [{"msg": "  hello  ", "level": "info"}]
        result = normalize_records(records, {"msg": "strip"})
        assert result[0]["msg"] == "hello"
        assert result[0]["level"] == "info"

    def test_bool_applied(self):
        records = [{"active": "true"}, {"active": "false"}]
        result = normalize_records(records, {"active": "bool"})
        assert result[0]["active"] is True
        assert result[1]["active"] is False

    def test_none_applied(self):
        records = [{"val": "null"}, {"val": "real"}]
        result = normalize_records(records, {"val": "none"})
        assert result[0]["val"] is None
        assert result[1]["val"] == "real"

    def test_multiple_fields(self):
        records = [{"msg": "  hi  ", "active": "yes"}]
        result = normalize_records(records, {"msg": "strip", "active": "bool"})
        assert result[0]["msg"] == "hi"
        assert result[0]["active"] is True

    def test_callable_spec(self):
        records = [{"level": "info"}]
        result = normalize_records(records, {"level": str.upper})
        assert result[0]["level"] == "INFO"

    def test_empty_records(self):
        assert normalize_records([], {"msg": "strip"}) == []

    def test_does_not_mutate_originals(self):
        records = [{"msg": "  hi  "}]
        normalize_records(records, {"msg": "strip"})
        assert records[0]["msg"] == "  hi  "

    def test_missing_field_unchanged(self):
        records = [{"level": "info"}]
        result = normalize_records(records, {"msg": "strip"})
        assert result[0] == {"level": "info"}
