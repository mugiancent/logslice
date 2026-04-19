"""Tests for logslice.differ."""
from logslice.differ import diff_records, changed_fields, summary


BEFORE = [
    {"id": "1", "level": "info", "msg": "ok"},
    {"id": "2", "level": "warn", "msg": "slow"},
    {"id": "3", "level": "error", "msg": "boom"},
]

AFTER = [
    {"id": "1", "level": "info", "msg": "ok"},
    {"id": "2", "level": "error", "msg": "very slow"},
    {"id": "4", "level": "debug", "msg": "new"},
]


class TestDiffRecords:
    def _run(self):
        return list(diff_records(BEFORE, AFTER, key="id"))

    def test_detects_removed(self):
        diffs = self._run()
        statuses = {d["key"]: d["status"] for d in diffs}
        assert statuses["3"] == "removed"

    def test_detects_added(self):
        diffs = self._run()
        statuses = {d["key"]: d["status"] for d in diffs}
        assert statuses["4"] == "added"

    def test_detects_changed(self):
        diffs = self._run()
        statuses = {d["key"]: d["status"] for d in diffs}
        assert statuses["2"] == "changed"

    def test_unchanged_not_included(self):
        diffs = self._run()
        keys = {d["key"] for d in diffs}
        assert "1" not in keys

    def test_empty_before(self):
        diffs = list(diff_records([], AFTER, key="id"))
        assert all(d["status"] == "added" for d in diffs)

    def test_empty_after(self):
        diffs = list(diff_records(BEFORE, [], key="id"))
        assert all(d["status"] == "removed" for d in diffs)

    def test_both_empty(self):
        assert list(diff_records([], [], key="id")) == []


class TestChangedFields:
    def test_detects_changed_field(self):
        result = changed_fields({"a": 1, "b": 2}, {"a": 1, "b": 3})
        assert ("b", 2, 3) in result

    def test_detects_added_field(self):
        result = changed_fields({"a": 1}, {"a": 1, "b": 2})
        assert ("b", None, 2) in result

    def test_detects_removed_field(self):
        result = changed_fields({"a": 1, "b": 2}, {"a": 1})
        assert ("b", 2, None) in result

    def test_identical_records_empty(self):
        assert changed_fields({"a": 1}, {"a": 1}) == []


class TestSummary:
    def test_counts_by_status(self):
        diffs = list(diff_records(BEFORE, AFTER, key="id"))
        s = summary(diffs)
        assert s["added"] == 1
        assert s["removed"] == 1
        assert s["changed"] == 1

    def test_empty_diffs(self):
        assert summary([]) == {"added": 0, "removed": 0, "changed": 0}
