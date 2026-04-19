"""Tests for logslice.importer."""
import pytest
from logslice.importer import from_jsonl, from_csv, from_tsv, load


class TestFromJsonl:
    def test_parses_valid_lines(self):
        text = '{"a":1}\n{"b":2}'
        records = list(from_jsonl(text))
        assert len(records) == 2
        assert records[0]["a"] == 1

    def test_skips_blank_lines(self):
        text = '{"a":1}\n\n{"b":2}'
        assert len(list(from_jsonl(text))) == 2

    def test_skips_invalid_json(self):
        text = '{"a":1}\nnot-json\n{"b":2}'
        assert len(list(from_jsonl(text))) == 2

    def test_skips_non_object_json(self):
        text = '[1,2,3]\n{"a":1}'
        records = list(from_jsonl(text))
        assert len(records) == 1

    def test_empty_string(self):
        assert list(from_jsonl("")) == []


class TestFromCsv:
    CSV = "name,age\nAlice,30\nBob,25\n"

    def test_header_becomes_keys(self):
        records = list(from_csv(self.CSV))
        assert records[0]["name"] == "Alice"

    def test_row_count(self):
        records = list(from_csv(self.CSV))
        assert len(records) == 2

    def test_custom_fields_override_header(self):
        data = "Alice,30\nBob,25\n"
        records = list(from_csv(data, fields=["name", "age"]))
        assert records[0]["name"] == "Alice"


class TestFromTsv:
    TSV = "name\tage\nAlice\t30\nBob\t25\n"

    def test_header_becomes_keys(self):
        records = list(from_tsv(self.TSV))
        assert records[0]["name"] == "Alice"

    def test_row_count(self):
        assert len(list(from_tsv(self.TSV))) == 2


class TestLoad:
    def test_jsonl_dispatch(self):
        records = list(load('{"x":1}', "jsonl"))
        assert records[0]["x"] == 1

    def test_csv_dispatch(self):
        records = list(load("a,b\n1,2\n", "csv"))
        assert records[0]["a"] == "1"

    def test_tsv_dispatch(self):
        records = list(load("a\tb\n1\t2\n", "tsv"))
        assert records[0]["a"] == "1"

    def test_unknown_format_raises(self):
        with pytest.raises(ValueError, match="Unknown import format"):
            list(load("", "xml"))
