"""Tests for logslice.exporter."""
import json
import pytest
from logslice.exporter import to_jsonl, to_csv, to_tsv, export

RECORDS = [
    {"ts": "2024-01-01T00:00:00Z", "level": "info", "msg": "start"},
    {"ts": "2024-01-01T00:01:00Z", "level": "error", "msg": "boom"},
]


class TestToJsonl:
    def test_each_line_is_valid_json(self):
        out = to_jsonl(RECORDS)
        lines = out.splitlines()
        assert len(lines) == 2
        assert json.loads(lines[0])["level"] == "info"

    def test_empty_returns_empty_string(self):
        assert to_jsonl([]) == ""

    def test_no_trailing_newline(self):
        out = to_jsonl(RECORDS)
        assert not out.endswith("\n")


class TestToCsv:
    def test_header_row_present(self):
        out = to_csv(RECORDS)
        assert out.splitlines()[0] == "ts,level,msg"

    def test_data_rows(self):
        out = to_csv(RECORDS)
        lines = out.splitlines()
        assert "error" in lines[2]

    def test_custom_field_order(self):
        out = to_csv(RECORDS, fields=["msg", "level"])
        assert out.splitlines()[0] == "msg,level"

    def test_missing_fields_become_empty(self):
        rows = [{"a": 1}, {"a": 2, "b": 3}]
        out = to_csv(rows, fields=["a", "b"])
        assert out.splitlines()[1] == "1,"

    def test_empty_records(self):
        assert to_csv([]) == ""


class TestToTsv:
    def test_tab_separated(self):
        out = to_tsv(RECORDS)
        assert "\t" in out.splitlines()[0]

    def test_empty_records(self):
        assert to_tsv([]) == ""


class TestExport:
    def test_jsonl_dispatch(self):
        out = export(RECORDS, "jsonl")
        assert json.loads(out.splitlines()[0])

    def test_csv_dispatch(self):
        out = export(RECORDS, "csv")
        assert out.splitlines()[0] == "ts,level,msg"

    def test_tsv_dispatch(self):
        out = export(RECORDS, "tsv")
        assert "\t" in out

    def test_unknown_format_raises(self):
        with pytest.raises(ValueError, match="Unknown export format"):
            export(RECORDS, "xml")
