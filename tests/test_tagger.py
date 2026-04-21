"""Tests for logslice.tagger."""

from __future__ import annotations

import pytest

from logslice.tagger import (
    apply_tags,
    tag_by_field,
    tag_by_pattern,
    tag_by_predicate,
)


class TestTagByField:
    def test_matching_value_adds_tag(self):
        rec = {"level": "error", "msg": "boom"}
        result = tag_by_field(rec, "level", "error", "is_error")
        assert result["tags"] == ["is_error"]

    def test_non_matching_value_unchanged(self):
        rec = {"level": "info"}
        result = tag_by_field(rec, "level", "error", "is_error")
        assert "tags" not in result

    def test_missing_field_unchanged(self):
        rec = {"msg": "hello"}
        result = tag_by_field(rec, "level", "error", "is_error")
        assert "tags" not in result

    def test_does_not_duplicate_tag(self):
        rec = {"level": "error", "tags": ["is_error"]}
        result = tag_by_field(rec, "level", "error", "is_error")
        assert result["tags"] == ["is_error"]

    def test_does_not_mutate_original(self):
        rec = {"level": "error"}
        tag_by_field(rec, "level", "error", "is_error")
        assert "tags" not in rec

    def test_custom_tag_field(self):
        rec = {"level": "error"}
        result = tag_by_field(rec, "level", "error", "is_error", tag_field="labels")
        assert result["labels"] == ["is_error"]
        assert "tags" not in result


class TestTagByPattern:
    def test_matching_pattern_adds_tag(self):
        rec = {"msg": "connection refused"}
        result = tag_by_pattern(rec, "msg", r"refused", "conn_error")
        assert "conn_error" in result["tags"]

    def test_non_matching_pattern_unchanged(self):
        rec = {"msg": "all good"}
        result = tag_by_pattern(rec, "msg", r"refused", "conn_error")
        assert "tags" not in result

    def test_missing_field_unchanged(self):
        rec = {"level": "error"}
        result = tag_by_pattern(rec, "msg", r"refused", "conn_error")
        assert "tags" not in result

    def test_partial_match_succeeds(self):
        rec = {"msg": "timeout: connection refused by host"}
        result = tag_by_pattern(rec, "msg", r"timeout", "slow")
        assert "slow" in result["tags"]


class TestTagByPredicate:
    def test_truthy_predicate_adds_tag(self):
        rec = {"status": 500}
        result = tag_by_predicate(rec, lambda r: r.get("status", 0) >= 500, "server_error")
        assert "server_error" in result["tags"]

    def test_falsy_predicate_unchanged(self):
        rec = {"status": 200}
        result = tag_by_predicate(rec, lambda r: r.get("status", 0) >= 500, "server_error")
        assert "tags" not in result


class TestApplyTags:
    def test_applies_multiple_rules(self):
        rec = {"level": "error", "status": 500}
        rules = [
            lambda r: tag_by_field(r, "level", "error", "is_error"),
            lambda r: tag_by_predicate(r, lambda x: x.get("status", 0) >= 500, "server_error"),
        ]
        results = apply_tags([rec], rules)
        assert "is_error" in results[0]["tags"]
        assert "server_error" in results[0]["tags"]

    def test_empty_records(self):
        assert apply_tags([], []) == []

    def test_no_rules_returns_unchanged(self):
        records = [{"a": 1}, {"b": 2}]
        assert apply_tags(records, []) == records
