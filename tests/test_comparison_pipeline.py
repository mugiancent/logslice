"""Tests for logslice.comparison_pipeline."""

import json
import pytest
from logslice.comparison_pipeline import compare_streams, compare_summary


LEFT = [
    '{"id": "1", "level": "info"}\n',
    '{"id": "2", "level": "warn"}\n',
]
RIGHT_CHANGED = [
    '{"id": "1", "level": "error"}\n',  # changed
    '{"id": "3", "level": "debug"}\n',  # added
]


def _parse_jsonl(text: str):
    return [json.loads(line) for line in text.splitlines() if line.strip()]


class TestCompareStreams:
    def test_returns_jsonl_string(self):
        result = compare_streams(LEFT, LEFT, key="id")
        records = _parse_jsonl(result)
        assert all(isinstance(r, dict) for r in records)

    def test_all_equal_when_identical(self):
        result = compare_streams(LEFT, LEFT, key="id")
        records = _parse_jsonl(result)
        assert all(r["status"] == "equal" for r in records)

    def test_detects_changed_and_added_and_removed(self):
        result = compare_streams(LEFT, RIGHT_CHANGED, key="id")
        records = _parse_jsonl(result)
        statuses = {r["key_value"]: r["status"] for r in records}
        assert statuses["1"] == "changed"
        assert statuses["2"] == "removed"
        assert statuses["3"] == "added"

    def test_only_filter_changed(self):
        result = compare_streams(LEFT, RIGHT_CHANGED, key="id", only="changed")
        records = _parse_jsonl(result)
        assert all(r["status"] == "changed" for r in records)
        assert len(records) == 1

    def test_only_filter_added(self):
        result = compare_streams(LEFT, RIGHT_CHANGED, key="id", only="added")
        records = _parse_jsonl(result)
        assert len(records) == 1
        assert records[0]["status"] == "added"

    def test_invalid_lines_skipped(self):
        left = ['not-json\n', '{"id": "1", "level": "info"}\n']
        result = compare_streams(left, LEFT, key="id")
        records = _parse_jsonl(result)
        assert any(r["key_value"] == "1" for r in records)

    def test_empty_streams(self):
        result = compare_streams([], [], key="id")
        assert result == ""


class TestCompareSummary:
    def test_returns_dict_with_counts(self):
        result = compare_summary(LEFT, RIGHT_CHANGED, key="id")
        assert isinstance(result, dict)
        assert result["changed"] == 1
        assert result["removed"] == 1
        assert result["added"] == 1
        assert result["equal"] == 0

    def test_all_equal_summary(self):
        result = compare_summary(LEFT, LEFT, key="id")
        assert result["equal"] == 2
        assert result["changed"] == 0
