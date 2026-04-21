"""Tests for logslice.scorer."""

import pytest

from logslice.scorer import (
    make_field_presence_rule,
    make_field_value_rule,
    make_pattern_rule,
    score_record,
    score_records,
    top_scored,
)

RECORDS = [
    {"level": "error", "msg": "disk full", "host": "web-1"},
    {"level": "warn",  "msg": "high memory", "host": "web-2"},
    {"level": "info",  "msg": "started"},
    {"level": "error", "msg": "connection refused", "host": "db-1"},
]


class TestMakeFieldPresenceRule:
    def test_field_present_returns_true(self):
        pred, weight = make_field_presence_rule("host", 2.0)
        assert pred({"host": "x"}) is True
        assert weight == 2.0

    def test_field_absent_returns_false(self):
        pred, _ = make_field_presence_rule("host")
        assert pred({"level": "info"}) is False


class TestMakeFieldValueRule:
    def test_matching_value_returns_true(self):
        pred, weight = make_field_value_rule("level", "error", 3.0)
        assert pred({"level": "error"}) is True
        assert weight == 3.0

    def test_non_matching_value_returns_false(self):
        pred, _ = make_field_value_rule("level", "error")
        assert pred({"level": "info"}) is False

    def test_missing_field_returns_false(self):
        pred, _ = make_field_value_rule("level", "error")
        assert pred({}) is False


class TestMakePatternRule:
    def test_pattern_matches(self):
        pred, weight = make_pattern_rule("msg", r"disk", 1.5)
        assert pred({"msg": "disk full"}) is True
        assert weight == 1.5

    def test_pattern_no_match(self):
        pred, _ = make_pattern_rule("msg", r"disk")
        assert pred({"msg": "started"}) is False

    def test_missing_field_returns_false(self):
        pred, _ = make_pattern_rule("msg", r"disk")
        assert pred({}) is False


class TestScoreRecord:
    def test_all_rules_match(self):
        rules = [
            make_field_value_rule("level", "error", 2.0),
            make_field_presence_rule("host", 1.0),
        ]
        assert score_record(RECORDS[0], rules) == 3.0

    def test_no_rules_match(self):
        rules = [make_field_value_rule("level", "critical", 5.0)]
        assert score_record(RECORDS[2], rules) == 0.0

    def test_partial_match(self):
        rules = [
            make_field_value_rule("level", "error", 2.0),
            make_field_presence_rule("host", 1.0),
        ]
        # RECORDS[2] has no 'host' and level is 'info'
        assert score_record(RECORDS[2], rules) == 0.0


class TestScoreRecords:
    def _rules(self):
        return [
            make_field_value_rule("level", "error", 3.0),
            make_field_presence_rule("host", 1.0),
        ]

    def test_returns_sorted_descending(self):
        results = score_records(RECORDS, self._rules())
        scores = [s for s, _ in results]
        assert scores == sorted(scores, reverse=True)

    def test_min_score_filters_out_low_scores(self):
        results = score_records(RECORDS, self._rules(), min_score=3.0)
        assert all(s >= 3.0 for s, _ in results)

    def test_empty_records_returns_empty(self):
        assert score_records([], self._rules()) == []


class TestTopScored:
    def _rules(self):
        return [make_field_value_rule("level", "error", 2.0)]

    def test_returns_top_n(self):
        results = top_scored(RECORDS, self._rules(), n=1)
        assert len(results) == 1
        assert results[0]["level"] == "error"

    def test_n_larger_than_results_returns_all_matching(self):
        results = top_scored(RECORDS, self._rules(), n=10, min_score=1.0)
        assert all(r["level"] == "error" for r in results)

    def test_invalid_n_raises(self):
        with pytest.raises(ValueError):
            top_scored(RECORDS, self._rules(), n=0)
