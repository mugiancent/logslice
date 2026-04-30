"""Tests for logslice.pivot."""
import pytest
from logslice.pivot import pivot_records, unpivot_records, wide_to_long


SAMPLE = [
    {"host": "a", "metric": "cpu", "value": 10},
    {"host": "a", "metric": "mem", "value": 80},
    {"host": "b", "metric": "cpu", "value": 20},
    {"host": "b", "metric": "mem", "value": 60},
]


class TestPivotRecords:
    def test_produces_one_row_per_index(self):
        result = pivot_records(SAMPLE, "host", "metric", "value")
        assert len(result) == 2

    def test_column_values_become_keys(self):
        result = pivot_records(SAMPLE, "host", "metric", "value")
        row_a = next(r for r in result if r["host"] == "a")
        assert row_a["cpu"] == 10
        assert row_a["mem"] == 80

    def test_fill_value_used_for_missing(self):
        partial = [
            {"host": "a", "metric": "cpu", "value": 5},
            {"host": "b", "metric": "mem", "value": 3},
        ]
        result = pivot_records(partial, "host", "metric", "value", fill_value=0)
        row_a = next(r for r in result if r["host"] == "a")
        assert row_a["mem"] == 0

    def test_empty_input_returns_empty(self):
        assert pivot_records([], "host", "metric", "value") == []

    def test_index_field_preserved(self):
        result = pivot_records(SAMPLE, "host", "metric", "value")
        for row in result:
            assert "host" in row


class TestUnpivotRecords:
    WIDE = [
        {"id": 1, "cpu": 10, "mem": 80},
        {"id": 2, "cpu": 20, "mem": 60},
    ]

    def test_produces_one_row_per_non_index_column(self):
        result = list(unpivot_records(self.WIDE, ["id"]))
        assert len(result) == 4

    def test_variable_and_value_fields_present(self):
        result = list(unpivot_records(self.WIDE, ["id"]))
        for row in result:
            assert "variable" in row
            assert "value" in row

    def test_custom_column_and_value_names(self):
        result = list(unpivot_records(self.WIDE, ["id"], column_field="k", value_field="v"))
        assert all("k" in r and "v" in r for r in result)

    def test_empty_input_yields_nothing(self):
        assert list(unpivot_records([], ["id"])) == []

    def test_index_field_value_preserved(self):
        result = list(unpivot_records(self.WIDE, ["id"]))
        ids = {r["id"] for r in result}
        assert ids == {1, 2}


class TestWideToLong:
    WIDE = [
        {"ts": "t1", "a": 1, "b": 2, "c": 3},
    ]

    def test_all_non_id_fields_expanded(self):
        result = list(wide_to_long(self.WIDE, id_field="ts"))
        assert len(result) == 3

    def test_subset_of_value_fields(self):
        result = list(wide_to_long(self.WIDE, id_field="ts", value_fields=["a", "b"]))
        assert len(result) == 2

    def test_id_field_present_in_each_row(self):
        result = list(wide_to_long(self.WIDE, id_field="ts"))
        assert all(r["ts"] == "t1" for r in result)

    def test_custom_column_and_value_names(self):
        result = list(wide_to_long(self.WIDE, id_field="ts", column_field="m", value_field="v"))
        assert all("m" in r and "v" in r for r in result)

    def test_missing_value_field_skipped(self):
        result = list(wide_to_long(self.WIDE, id_field="ts", value_fields=["a", "z"]))
        metrics = [r["metric"] for r in result]
        assert "z" not in metrics
