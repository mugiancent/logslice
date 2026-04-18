"""Tests for logslice.pipeline (updated to cover sampling integration)."""
import json
import pytest
from logslice.pipeline import process_lines


def make_lines(n: int) -> list[str]:
    return [
        json.dumps({"ts": f"2024-01-01T00:00:{i:02d}Z", "level": "info", "id": str(i)})
        for i in range(n)
    ]


class TestProcessLines:
    def test_parses_and_formats_all_valid(self):
        lines = make_lines(3)
        result = list(process_lines(lines))
        assert len(result) == 3
        for r in result:
            assert json.loads(r)

    def test_invalid_lines_skipped(self):
        lines = ["not json", make_lines(1)[0]]
        result = list(process_lines(lines))
        assert len(result) == 1

    def test_start_filter(self):
        lines = make_lines(5)
        result = list(process_lines(lines, start="2024-01-01T00:00:03Z"))
        assert len(result) == 2

    def test_end_filter(self):
        lines = make_lines(5)
        result = list(process_lines(lines, end="2024-01-01T00:00:01Z"))
        assert len(result) == 2

    def test_field_filter(self):
        lines = [
            json.dumps({"level": "error", "msg": "bad"}),
            json.dumps({"level": "info", "msg": "ok"}),
        ]
        result = list(process_lines(lines, field_filter=("level", "error")))
        assert len(result) == 1
        assert json.loads(result[0])["msg"] == "bad"

    def test_sample_n_reduces_output(self):
        lines = make_lines(10)
        result = list(process_lines(lines, sample_n=2))
        assert len(result) == 5

    def test_sample_n_1_keeps_all(self):
        lines = make_lines(6)
        result = list(process_lines(lines, sample_n=1))
        assert len(result) == 6

    def test_empty_input(self):
        assert list(process_lines([])) == []
