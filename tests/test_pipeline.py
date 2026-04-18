"""Tests for logslice.pipeline module."""
import json
import pytest
from logslice.pipeline import process_lines

LINES = [
    '{"ts":"2024-06-01T10:00:00Z","level":"info","msg":"start","svc":"api"}\n',
    '{"ts":"2024-06-01T11:00:00Z","level":"error","msg":"fail","svc":"db"}\n',
    '{"ts":"2024-06-01T12:00:00Z","level":"info","msg":"done","svc":"api"}\n',
    'not json at all\n',
]


class TestProcessLines:
    def test_parses_and_formats_all_valid(self):
        results = list(process_lines(LINES, fmt="json"))
        assert len(results) == 3
        for r in results:
            obj = json.loads(r)
            assert "ts" in obj

    def test_invalid_lines_skipped(self):
        results = list(process_lines(LINES, fmt="json"))
        assert len(results) == 3

    def test_start_filter(self):
        results = list(process_lines(LINES, start="2024-06-01T11:00:00Z", fmt="json"))
        assert len(results) == 2

    def test_end_filter(self):
        results = list(process_lines(LINES, end="2024-06-01T10:59:59Z", fmt="json"))
        assert len(results) == 1

    def test_field_filter(self):
        results = list(process_lines(LINES, field_filters=["svc=api"], fmt="json"))
        assert len(results) == 2
        for r in results:
            assert json.loads(r)["svc"] == "api"

    def test_pick_fields(self):
        results = list(process_lines(LINES, pick=["level", "msg"], fmt="json"))
        for r in results:
            obj = json.loads(r)
            assert set(obj.keys()) == {"level", "msg"}

    def test_drop_fields(self):
        results = list(process_lines(LINES, drop=["svc"], fmt="json"))
        for r in results:
            assert "svc" not in json.loads(r)

    def test_logfmt_output(self):
        results = list(process_lines(LINES[:1], fmt="logfmt"))
        assert "level=info" in results[0]

    def test_empty_input(self):
        assert list(process_lines([], fmt="json")) == []
