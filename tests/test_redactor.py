"""Tests for logslice.redactor."""

import pytest
from logslice.redactor import redact_fields, redact_pattern, apply_redactions, DEFAULT_MASK


class TestRedactFields:
    def test_masks_specified_field(self):
        rec = {"user": "alice", "msg": "hello"}
        result = redact_fields(rec, ["user"])
        assert result["user"] == DEFAULT_MASK
        assert result["msg"] == "hello"

    def test_missing_field_ignored(self):
        rec = {"msg": "hello"}
        result = redact_fields(rec, ["password"])
        assert result == {"msg": "hello"}

    def test_custom_mask(self):
        rec = {"token": "abc123"}
        result = redact_fields(rec, ["token"], mask="[REDACTED]")
        assert result["token"] == "[REDACTED]"

    def test_does_not_mutate_original(self):
        rec = {"user": "alice"}
        redact_fields(rec, ["user"])
        assert rec["user"] == "alice"

    def test_multiple_fields(self):
        rec = {"a": 1, "b": 2, "c": 3}
        result = redact_fields(rec, ["a", "c"])
        assert result["a"] == DEFAULT_MASK
        assert result["c"] == DEFAULT_MASK
        assert result["b"] == 2


class TestRedactPattern:
    def test_replaces_matching_substring(self):
        rec = {"msg": "user email is foo@example.com today"}
        result = redact_pattern(rec, r"[\w.+-]+@[\w-]+\.[\w.]+")
        assert result["msg"] == "user email is *** today"

    def test_non_string_fields_untouched(self):
        rec = {"count": 42, "msg": "hello 123"}
        result = redact_pattern(rec, r"\d+")
        assert result["count"] == 42
        assert result["msg"] == "hello ***"

    def test_scoped_to_specified_fields(self):
        rec = {"a": "secret123", "b": "other123"}
        result = redact_pattern(rec, r"\d+", fields=["a"])
        assert result["a"] == "secret***"
        assert result["b"] == "other123"

    def test_no_match_leaves_value(self):
        rec = {"msg": "nothing here"}
        result = redact_pattern(rec, r"\d+")
        assert result["msg"] == "nothing here"


class TestApplyRedactions:
    def test_combines_field_and_pattern_redactions(self):
        rec = {"user": "alice", "msg": "token=abc123"}
        result = apply_redactions(rec, redact_field_list=["user"], redact_patterns=[r"token=\S+"])
        assert result["user"] == DEFAULT_MASK
        assert result["msg"] == "***"

    def test_no_redactions_returns_copy(self):
        rec = {"a": "b"}
        result = apply_redactions(rec)
        assert result == rec
        assert result is not rec

    def test_custom_mask_propagated(self):
        rec = {"pw": "hunter2", "msg": "pw=hunter2"}
        result = apply_redactions(rec, redact_field_list=["pw"], redact_patterns=[r"pw=\S+"], mask="<hidden>")
        assert result["pw"] == "<hidden>"
        assert result["msg"] == "<hidden>"
