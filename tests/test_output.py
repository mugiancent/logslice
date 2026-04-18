"""Tests for logslice.output module."""
import io
import json
import pytest

from logslice.output import format_record, write_records, _to_logfmt


SAMPLE = {"level": "info", "msg": "hello world", "ts": "2024-01-01T00:00:00Z"}


class TestFormatRecordJSON:
    def test_produces_valid_json(self):
        result = format_record(SAMPLE, fmt="json")
        parsed = json.loads(result)
        assert parsed == SAMPLE

    def test_single_line(self):
        result = format_record(SAMPLE, fmt="json")
        assert "\n" not in result


class TestFormatRecordLogfmt:
    def test_simple_values(self):
        record = {"level": "info", "code": "200"}
        result = format_record(record, fmt="logfmt")
        assert "level=info" in result
        assert "code=200" in result

    def test_value_with_space_is_quoted(self):
        record = {"msg": "hello world"}
        result = format_record(record, fmt="logfmt")
        assert 'msg="hello world"' in result

    def test_none_value(self):
        record = {"key": None}
        result = _to_logfmt(record)
        assert "key=" in result


class TestFormatRecordPretty:
    def test_contains_keys(self):
        result = format_record(SAMPLE, fmt="pretty")
        assert "level" in result
        assert "info" in result

    def test_starts_with_separator(self):
        result = format_record(SAMPLE, fmt="pretty")
        assert result.startswith("---")


class TestFormatRecordInvalid:
    def test_unknown_format_raises(self):
        with pytest.raises(ValueError, match="Unknown output format"):
            format_record(SAMPLE, fmt="xml")


class TestWriteRecords:
    def test_writes_all_records(self):
        buf = io.StringIO()
        records = [{"a": "1"}, {"b": "2"}, {"c": "3"}]
        count = write_records(records, fmt="json", output=buf)
        assert count == 3
        lines = buf.getvalue().strip().split("\n")
        assert len(lines) == 3

    def test_returns_zero_for_empty(self):
        buf = io.StringIO()
        count = write_records([], output=buf)
        assert count == 0

    def test_each_line_valid_json(self):
        buf = io.StringIO()
        records = [{"x": i} for i in range(5)]
        write_records(records, fmt="json", output=buf)
        for line in buf.getvalue().strip().split("\n"):
            json.loads(line)
