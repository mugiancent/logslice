"""Edge-case tests for pivot and unpivot operations."""
import pytest
from logslice.pivot import pivot_records, unpivot_records, wide_to_long


class TestPivotEdgeCases:
    def test_none_index_value_handled(self):
        records = [{"host": None, "metric": "cpu", "value": 5}]
        result = pivot_records(records, "host", "metric", "value")
        assert len(result) == 1
        assert result[0]["host"] is None

    def test_duplicate_index_column_pair_last_wins(self):
        records = [
            {"host": "a", "metric": "cpu", "value": 1},
            {"host": "a", "metric": "cpu", "value": 99},
        ]
        result = pivot_records(records, "host", "metric", "value")
        assert result[0]["cpu"] == 99

    def test_single_record_single_column(self):
        records = [{"host": "x", "metric": "load", "value": 0.5}]
        result = pivot_records(records, "host", "metric", "value")
        assert result == [{"host": "x", "load": 0.5}]

    def test_missing_value_field_uses_none(self):
        records = [{"host": "a", "metric": "cpu"}]
        result = pivot_records(records, "host", "metric", "value")
        assert result[0]["cpu"] is None

    def test_column_order_preserved(self):
        records = [
            {"h": "a", "k": "z", "v": 1},
            {"h": "a", "k": "m", "v": 2},
        ]
        result = pivot_records(records, "h", "k", "v")
        keys = [k for k in result[0] if k != "h"]
        assert keys == ["z", "m"]


class TestUnpivotEdgeCases:
    def test_multiple_index_fields_preserved(self):
        records = [{"host": "a", "env": "prod", "cpu": 10, "mem": 80}]
        result = list(unpivot_records(records, ["host", "env"]))
        for row in result:
            assert row["host"] == "a"
            assert row["env"] == "prod"

    def test_record_with_only_index_fields_yields_nothing(self):
        records = [{"host": "a"}]
        result = list(unpivot_records(records, ["host"]))
        assert result == []

    def test_none_value_preserved(self):
        records = [{"id": 1, "x": None}]
        result = list(unpivot_records(records, ["id"]))
        assert result[0]["value"] is None

    def test_integer_column_names_handled(self):
        records = [{"id": 1, 2: "two"}]
        result = list(unpivot_records(records, ["id"]))
        assert len(result) == 1
        assert result[0]["variable"] == 2


class TestWideToLongEdgeCases:
    def test_empty_value_fields_list_yields_nothing(self):
        records = [{"ts": "t1", "a": 1}]
        result = list(wide_to_long(records, id_field="ts", value_fields=[]))
        assert result == []

    def test_id_field_missing_from_record(self):
        records = [{"a": 1, "b": 2}]
        result = list(wide_to_long(records, id_field="ts"))
        assert all(r["ts"] is None for r in result)

    def test_multiple_records_correct_count(self):
        records = [
            {"ts": "t1", "x": 1, "y": 2},
            {"ts": "t2", "x": 3, "y": 4},
        ]
        result = list(wide_to_long(records, id_field="ts"))
        assert len(result) == 4
