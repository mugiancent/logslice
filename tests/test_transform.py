"""Tests for logslice.transform module."""
import pytest
from logslice.transform import (
    pick_fields,
    drop_fields,
    rename_field,
    add_field,
    apply_transforms,
)

SAMPLE = {"level": "info", "msg": "hello", "ts": "2024-01-01T00:00:00Z", "svc": "api"}


class TestPickFields:
    def test_keeps_requested_fields(self):
        result = pick_fields(SAMPLE, ["level", "msg"])
        assert result == {"level": "info", "msg": "hello"}

    def test_missing_fields_ignored(self):
        result = pick_fields(SAMPLE, ["level", "nonexistent"])
        assert result == {"level": "info"}

    def test_empty_fields_list(self):
        assert pick_fields(SAMPLE, []) == {}


class TestDropFields:
    def test_removes_requested_fields(self):
        result = drop_fields(SAMPLE, ["ts", "svc"])
        assert result == {"level": "info", "msg": "hello"}

    def test_missing_fields_ignored(self):
        result = drop_fields(SAMPLE, ["nonexistent"])
        assert result == SAMPLE

    def test_empty_drop_list(self):
        assert drop_fields(SAMPLE, []) == SAMPLE


class TestRenameField:
    def test_renames_existing_field(self):
        result = rename_field(SAMPLE, "msg", "message")
        assert "message" in result
        assert "msg" not in result
        assert result["message"] == "hello"

    def test_missing_field_returns_copy(self):
        result = rename_field(SAMPLE, "nope", "new")
        assert result == SAMPLE
        assert "new" not in result


class TestAddField:
    def test_adds_new_field(self):
        result = add_field(SAMPLE, "env", "prod")
        assert result["env"] == "prod"

    def test_original_unchanged(self):
        add_field(SAMPLE, "env", "prod")
        assert "env" not in SAMPLE


class TestApplyTransforms:
    def test_pick_only(self):
        result = apply_transforms(SAMPLE, pick=["level", "msg"])
        assert set(result.keys()) == {"level", "msg"}

    def test_drop_only(self):
        result = apply_transforms(SAMPLE, drop=["ts"])
        assert "ts" not in result

    def test_rename_only(self):
        result = apply_transforms(SAMPLE, rename={"msg": "message"})
        assert "message" in result and "msg" not in result

    def test_pick_then_drop(self):
        result = apply_transforms(SAMPLE, pick=["level", "msg", "ts"], drop=["ts"])
        assert set(result.keys()) == {"level", "msg"}

    def test_no_transforms_returns_copy(self):
        result = apply_transforms(SAMPLE)
        assert result == SAMPLE
