"""Tests for logslice.parser module."""

import pytest
from logslice.parser import parse_line


class TestParseLineJSON:
    def test_valid_json_object(self):
        line = '{"level": "info", "msg": "started", "ts": "2024-01-01T00:00:00Z"}'
        result = parse_line(line)
        assert result == {"level": "info", "msg": "started", "ts": "2024-01-01T00:00:00Z"}

    def test_invalid_json_falls_through(self):
        line = '{bad json'
        result = parse_line(line)
        assert result is None

    def test_empty_json_object(self):
        result = parse_line("{}")
        assert result == {}


class TestParseLineLogfmt:
    def test_simple_key_value(self):
        result = parse_line("level=info msg=started")
        assert result == {"level": "info", "msg": "started"}

    def test_quoted_value(self):
        result = parse_line('level=info msg="server started successfully"')
        assert result == {"level": "info", "msg": "server started successfully"}

    def test_boolean_flag(self):
        result = parse_line("verbose level=debug")
        assert result == {"verbose": True, "level": "debug"}

    def test_mixed_quoted_and_unquoted(self):
        result = parse_line('ts=2024-01-01 msg="hello world" code=200')
        assert result == {"ts": "2024-01-01", "msg": "hello world", "code": "200"}

    def test_empty_string_returns_none(self):
        assert parse_line("") is None
        assert parse_line("   ") is None

    def test_whitespace_stripped(self):
        result = parse_line("  level=warn  ")
        assert result == {"level": "warn"}
