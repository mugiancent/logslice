"""Tests for logslice.join_pipeline."""

import json
import pytest
from logslice.join_pipeline import join_streams


LEFT_LINES = [
    '{"id": "1", "user": "alice"}',
    '{"id": "2", "user": "bob"}',
    '{"id": "3", "user": "carol"}',
    "not valid json",
]

RIGHT_LINES = [
    '{"id": "1", "level": "info"}',
    '{"id": "2", "level": "warn"}',
    '{"id": "99", "level": "error"}',
]


class TestJoinStreams:
    def test_inner_join_returns_matching_records(self):
        result = list(join_streams(LEFT_LINES, RIGHT_LINES, on="id"))
        assert len(result) == 2

    def test_output_is_valid_json_by_default(self):
        result = list(join_streams(LEFT_LINES, RIGHT_LINES, on="id"))
        for line in result:
            parsed = json.loads(line)
            assert isinstance(parsed, dict)

    def test_right_fields_prefixed(self):
        result = list(join_streams(LEFT_LINES, RIGHT_LINES, on="id"))
        records = [json.loads(r) for r in result]
        assert all("right_level" in r for r in records)

    def test_custom_prefix(self):
        result = list(
            join_streams(LEFT_LINES, RIGHT_LINES, on="id", right_prefix="r_")
        )
        records = [json.loads(r) for r in result]
        assert all("r_level" in r for r in records)

    def test_invalid_lines_skipped(self):
        result = list(join_streams(LEFT_LINES, RIGHT_LINES, on="id"))
        # carol (id=3) has no match; invalid JSON line is silently dropped
        users = [json.loads(r)["user"] for r in result]
        assert "alice" in users
        assert "bob" in users

    def test_left_join_includes_unmatched_left(self):
        result = list(
            join_streams(LEFT_LINES, RIGHT_LINES, on="id", mode="left")
        )
        # alice, bob, carol — invalid JSON line still dropped
        assert len(result) == 3

    def test_left_join_unmatched_has_no_right_fields(self):
        result = list(
            join_streams(LEFT_LINES, RIGHT_LINES, on="id", mode="left")
        )
        records = [json.loads(r) for r in result]
        carol = next(r for r in records if r["user"] == "carol")
        assert "right_level" not in carol

    def test_logfmt_output_format(self):
        result = list(
            join_streams(LEFT_LINES, RIGHT_LINES, on="id", fmt="logfmt")
        )
        assert len(result) == 2
        # logfmt lines should contain key=value pairs
        assert "user=" in result[0]

    def test_empty_right_inner_returns_nothing(self):
        result = list(join_streams(LEFT_LINES, [], on="id"))
        assert result == []

    def test_empty_left_returns_nothing(self):
        result = list(join_streams([], RIGHT_LINES, on="id"))
        assert result == []
