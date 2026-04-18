"""Tests for logslice.schema."""
import pytest
from logslice.schema import Schema


SIMPLE_FIELDS = [
    {"name": "timestamp", "required": True, "type": str},
    {"name": "level", "required": True, "pattern": r"info|warn|error"},
    {"name": "count", "type": int},
]


class TestSchema:
    def setup_method(self):
        self.schema = Schema(SIMPLE_FIELDS)

    def test_valid_record_passes(self):
        record = {"timestamp": "2024-01-01T00:00:00Z", "level": "info", "count": 3}
        assert self.schema.is_valid(record) is True

    def test_missing_required_field_fails(self):
        record = {"level": "info"}
        errors = self.schema.validate(record)
        fields = [e["field"] for e in errors]
        assert "timestamp" in fields

    def test_wrong_type_fails(self):
        record = {"timestamp": "t", "level": "info", "count": "not-int"}
        errors = self.schema.validate(record)
        assert any(e["field"] == "count" for e in errors)

    def test_bad_pattern_fails(self):
        record = {"timestamp": "t", "level": "debug"}
        errors = self.schema.validate(record)
        assert any(e["field"] == "level" for e in errors)

    def test_optional_field_absent_passes(self):
        record = {"timestamp": "t", "level": "warn"}
        assert self.schema.is_valid(record) is True

    def test_from_dict(self):
        spec = {"fields": [{"name": "msg", "required": True}]}
        schema = Schema.from_dict(spec)
        assert schema.is_valid({"msg": "hello"}) is True
        assert schema.is_valid({}) is False

    def test_empty_schema_accepts_anything(self):
        schema = Schema([])
        assert schema.is_valid({}) is True
        assert schema.is_valid({"x": 1}) is True
