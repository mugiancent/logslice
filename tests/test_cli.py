"""Tests for logslice.cli module."""
import io
import json
import sys
import pytest
from unittest.mock import patch

from logslice.cli import build_parser, run


JSON_LINES = [
    '{"ts": "2024-01-01T10:00:00Z", "level": "info", "msg": "start"}\n',
    '{"ts": "2024-01-01T11:00:00Z", "level": "warn", "msg": "mid"}\n',
    '{"ts": "2024-01-01T12:00:00Z", "level": "info", "msg": "end"}\n',
]


class TestBuildParser:
    def test_defaults(self):
        p = build_parser()
        args = p.parse_args([])
        assert args.format == "json"
        assert args.fields == []
        assert args.start is None
        assert args.end is None

    def test_format_choices(self):
        p = build_parser()
        args = p.parse_args(["--format", "logfmt"])
        assert args.format == "logfmt"

    def test_invalid_format_exits(self):
        p = build_parser()
        with pytest.raises(SystemExit):
            p.parse_args(["--format", "xml"])


class TestRunFromStdin:
    def _run_with_input(self, lines, extra_args=None):
        argv = extra_args or []
        buf = io.StringIO()
        with patch("sys.stdin", io.StringIO("".join(lines))), \
             patch("sys.stdout", buf), \
             patch("sys.stderr", io.StringIO()):
            code = run(argv)
        return code, buf.getvalue()

    def test_all_records_returned(self):
        code, out = self._run_with_input(JSON_LINES)
        assert code == 0
        records = [json.loads(l) for l in out.strip().split("\n") if l]
        assert len(records) == 3

    def test_field_filter(self):
        code, out = self._run_with_input(JSON_LINES, ["--field", "level=warn"])
        assert code == 0
        records = [json.loads(l) for l in out.strip().split("\n") if l]
        assert len(records) == 1
        assert records[0]["level"] == "warn"

    def test_invalid_field_expr_returns_error(self):
        with patch("sys.stdin", io.StringIO("".join(JSON_LINES))), \
             patch("sys.stderr", io.StringIO()):
            code = run(["--field", "badexpr"])
        assert code == 1

    def test_missing_file_returns_error(self):
        with patch("sys.stderr", io.StringIO()):
            code = run(["nonexistent_file_xyz.log"])
        assert code == 1
