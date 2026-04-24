"""Tests for logslice.annotation_pipeline."""
import io
import json
import pytest
from logslice.annotation_pipeline import annotate_stream

LINES = [
    '{"level": "info", "msg": "server started"}\n',
    '{"level": "error", "msg": "timeout after 30s"}\n',
    '{"level": "info", "msg": "request ok"}\n',
    "not valid json\n",
]


def _run(**kwargs) -> list:
    buf = io.StringIO()
    annotate_stream(LINES, out=buf, **kwargs)
    buf.seek(0)
    return [json.loads(line) for line in buf if line.strip()]


class TestAnnotateStream:
    def test_invalid_lines_skipped(self):
        result = _run()
        assert len(result) == 3

    def test_add_index(self):
        result = _run(add_index=True)
        assert result[0]["_index"] == 0
        assert result[2]["_index"] == 2

    def test_add_index_custom_field(self):
        result = _run(add_index=True, index_field="seq")
        assert "seq" in result[0]
        assert "_index" not in result[0]

    def test_flag_field_added(self):
        result = _run(
            flag_field="_error",
            flag_source="level",
            flag_pattern="^error$",
        )
        assert result[1]["_error"] is True
        assert result[0]["_error"] is False

    def test_match_field_added(self):
        result = _run(
            match_field="_duration",
            match_source="msg",
            match_pattern=r"\d+s",
        )
        assert result[1]["_duration"] == "30s"
        assert result[0]["_duration"] is None

    def test_returns_record_count(self):
        buf = io.StringIO()
        count = annotate_stream(LINES, out=buf)
        assert count == 3

    def test_empty_input_returns_zero(self):
        buf = io.StringIO()
        count = annotate_stream([], out=buf)
        assert count == 0

    def test_combined_annotations(self):
        result = _run(
            add_index=True,
            flag_field="_err",
            flag_source="level",
            flag_pattern="error",
            match_field="_num",
            match_source="msg",
            match_pattern=r"\d+",
        )
        assert "_index" in result[0]
        assert "_err" in result[0]
        assert "_num" in result[0]
