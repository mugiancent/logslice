"""Tests for logslice.pivot_pipeline."""
import json
import pytest
from logslice.pivot_pipeline import pivot_stream, unpivot_stream, wide_to_long_stream


def _lines(records):
    return [json.dumps(r) for r in records]


SAMPLE = [
    {"host": "a", "metric": "cpu", "value": 10},
    {"host": "a", "metric": "mem", "value": 80},
    {"host": "b", "metric": "cpu", "value": 20},
    {"host": "b", "metric": "mem", "value": 60},
]


class TestPivotStream:
    def test_returns_string(self):
        out = pivot_stream(_lines(SAMPLE), "host", "metric", "value")
        assert isinstance(out, str)

    def test_output_lines_are_valid_json(self):
        out = pivot_stream(_lines(SAMPLE), "host", "metric", "value")
        for line in out.splitlines():
            assert json.loads(line)

    def test_one_row_per_host(self):
        out = pivot_stream(_lines(SAMPLE), "host", "metric", "value")
        assert len(out.splitlines()) == 2

    def test_invalid_lines_skipped(self):
        lines = ["not json"] + _lines(SAMPLE)
        out = pivot_stream(lines, "host", "metric", "value")
        assert len(out.splitlines()) == 2

    def test_empty_input_returns_empty_string(self):
        assert pivot_stream([], "host", "metric", "value") == ""


class TestUnpivotStream:
    WIDE = [
        {"id": 1, "cpu": 10, "mem": 80},
        {"id": 2, "cpu": 20, "mem": 60},
    ]

    def test_returns_string(self):
        out = unpivot_stream(_lines(self.WIDE), ["id"])
        assert isinstance(out, str)

    def test_output_lines_are_valid_json(self):
        out = unpivot_stream(_lines(self.WIDE), ["id"])
        for line in out.splitlines():
            json.loads(line)

    def test_four_rows_for_two_wide_records(self):
        out = unpivot_stream(_lines(self.WIDE), ["id"])
        assert len(out.splitlines()) == 4

    def test_empty_input_returns_empty_string(self):
        assert unpivot_stream([], ["id"]) == ""


class TestWideToLongStream:
    WIDE = [{"ts": "t1", "a": 1, "b": 2}]

    def test_returns_string(self):
        out = wide_to_long_stream(_lines(self.WIDE), id_field="ts")
        assert isinstance(out, str)

    def test_output_lines_are_valid_json(self):
        out = wide_to_long_stream(_lines(self.WIDE), id_field="ts")
        for line in out.splitlines():
            json.loads(line)

    def test_two_rows_for_two_value_fields(self):
        out = wide_to_long_stream(_lines(self.WIDE), id_field="ts")
        assert len(out.splitlines()) == 2

    def test_subset_value_fields(self):
        out = wide_to_long_stream(_lines(self.WIDE), id_field="ts", value_fields=["a"])
        assert len(out.splitlines()) == 1
