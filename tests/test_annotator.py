"""Tests for logslice.annotator."""
import pytest
from logslice.annotator import (
    annotate_with_index,
    annotate_with_line_number,
    annotate_with_flag,
    annotate_with_match,
    apply_annotations,
)

RECORDS = [
    {"level": "info", "msg": "started"},
    {"level": "error", "msg": "failed: code 500"},
    {"level": "info", "msg": "done"},
]


class TestAnnotateWithIndex:
    def test_adds_index_field(self):
        result = annotate_with_index(RECORDS)
        assert [r["_index"] for r in result] == [0, 1, 2]

    def test_custom_field_name(self):
        result = annotate_with_index(RECORDS, field="seq")
        assert "seq" in result[0]

    def test_custom_start(self):
        result = annotate_with_index(RECORDS, start=10)
        assert result[0]["_index"] == 10
        assert result[2]["_index"] == 12

    def test_does_not_mutate_original(self):
        originals = [{"a": 1}]
        annotate_with_index(originals)
        assert "_index" not in originals[0]

    def test_empty_input(self):
        assert annotate_with_index([]) == []


class TestAnnotateWithLineNumber:
    def test_starts_at_one(self):
        result = annotate_with_line_number(RECORDS)
        assert result[0]["_line"] == 1
        assert result[-1]["_line"] == 3


class TestAnnotateWithFlag:
    def test_true_when_predicate_matches(self):
        result = annotate_with_flag(RECORDS, lambda r: r["level"] == "error")
        flags = [r["_flagged"] for r in result]
        assert flags == [False, True, False]

    def test_custom_true_false_values(self):
        result = annotate_with_flag(
            RECORDS,
            lambda r: r["level"] == "error",
            true_value="yes",
            false_value="no",
        )
        assert result[1]["_flagged"] == "yes"
        assert result[0]["_flagged"] == "no"

    def test_custom_field_name(self):
        result = annotate_with_flag(RECORDS, lambda r: True, field="ok")
        assert "ok" in result[0]

    def test_empty_input(self):
        assert annotate_with_flag([], lambda r: True) == []


class TestAnnotateWithMatch:
    def test_captures_match(self):
        result = annotate_with_match(RECORDS, "msg", r"\d+")
        assert result[1]["_match"] == "500"

    def test_no_match_returns_none(self):
        result = annotate_with_match(RECORDS, "msg", r"\d+")
        assert result[0]["_match"] is None

    def test_custom_no_match_value(self):
        result = annotate_with_match(RECORDS, "msg", r"\d+", no_match_value="N/A")
        assert result[0]["_match"] == "N/A"

    def test_missing_source_field(self):
        result = annotate_with_match([{"x": 1}], "msg", r"\d+")
        assert result[0]["_match"] is None


class TestApplyAnnotations:
    def test_applies_in_order(self):
        import functools

        fn1 = functools.partial(annotate_with_index, field="_index")
        fn2 = functools.partial(annotate_with_line_number, field="_line")
        result = apply_annotations(RECORDS, [fn1, fn2])
        assert "_index" in result[0]
        assert "_line" in result[0]

    def test_empty_annotations_returns_records(self):
        result = apply_annotations(RECORDS, [])
        assert len(result) == len(RECORDS)
