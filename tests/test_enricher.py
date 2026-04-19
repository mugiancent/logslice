"""Tests for logslice.enricher."""

import pytest
from logslice.enricher import (
    add_derived_field,
    add_static_field,
    add_regex_capture,
    apply_enrichments,
)


class TestAddDerivedField:
    def test_applies_function_to_source(self):
        enrich = add_derived_field("upper_msg", "msg", str.upper)
        result = enrich({"msg": "hello"})
        assert result["upper_msg"] == "HELLO"

    def test_missing_source_returns_unchanged(self):
        enrich = add_derived_field("x", "missing", str.upper)
        record = {"msg": "hi"}
        assert enrich(record) == record

    def test_does_not_mutate_original(self):
        enrich = add_derived_field("n", "val", lambda v: v * 2)
        original = {"val": 3}
        enrich(original)
        assert "n" not in original


class TestAddStaticField:
    def test_adds_field(self):
        enrich = add_static_field("env", "production")
        result = enrich({"msg": "hi"})
        assert result["env"] == "production"

    def test_overwrites_existing(self):
        enrich = add_static_field("env", "staging")
        result = enrich({"env": "production"})
        assert result["env"] == "staging"

    def test_does_not_mutate_original(self):
        enrich = add_static_field("k", "v")
        original = {}
        enrich(original)
        assert "k" not in original


class TestAddRegexCapture:
    def test_captures_group(self):
        enrich = add_regex_capture("request_id", "msg", r"req=([\w-]+)")
        result = enrich({"msg": "start req=abc-123 end"})
        assert result["request_id"] == "abc-123"

    def test_no_match_returns_unchanged(self):
        enrich = add_regex_capture("rid", "msg", r"req=([\w-]+)")
        record = {"msg": "nothing here"}
        assert enrich(record) == record

    def test_missing_source_returns_unchanged(self):
        enrich = add_regex_capture("rid", "msg", r"req=([\w-]+)")
        record = {"level": "info"}
        assert enrich(record) == record

    def test_non_string_source_returns_unchanged(self):
        enrich = add_regex_capture("rid", "code", r"(\d+)")
        record = {"code": 404}
        assert enrich(record) == record

    def test_named_group(self):
        enrich = add_regex_capture("rid", "msg", r"req=(?P<id>[\w-]+)", group="id")
        result = enrich({"msg": "req=xyz"})
        assert result["rid"] == "xyz"


class TestApplyEnrichments:
    def test_applies_all_enrichers(self):
        enrichers = [
            add_static_field("env", "test"),
            add_derived_field("upper", "msg", str.upper),
        ]
        records = [{"msg": "hello"}]
        results = list(apply_enrichments(records, enrichers))
        assert results[0]["env"] == "test"
        assert results[0]["upper"] == "HELLO"

    def test_empty_enrichers(self):
        records = [{"msg": "hi"}]
        results = list(apply_enrichments(records, []))
        assert results == [{"msg": "hi"}]

    def test_empty_records(self):
        results = list(apply_enrichments([], [add_static_field("k", "v")]))
        assert results == []
