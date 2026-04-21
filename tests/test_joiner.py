"""Tests for logslice.joiner."""

import pytest
from logslice.joiner import inner_join, left_join, cross_join


LEFT = [
    {"id": "1", "name": "alice"},
    {"id": "2", "name": "bob"},
    {"id": "3", "name": "carol"},
]

RIGHT = [
    {"id": "1", "score": 10},
    {"id": "2", "score": 20},
    {"id": "4", "score": 40},
]


class TestInnerJoin:
    def test_only_matching_rows_returned(self):
        result = list(inner_join(LEFT, RIGHT, on="id"))
        assert len(result) == 2

    def test_merged_fields_present(self):
        result = list(inner_join(LEFT, RIGHT, on="id"))
        assert result[0] == {"id": "1", "name": "alice", "right_score": 10}
        assert result[1] == {"id": "2", "name": "bob", "right_score": 20}

    def test_custom_prefix(self):
        result = list(inner_join(LEFT, RIGHT, on="id", right_prefix="r_"))
        assert "r_score" in result[0]

    def test_empty_right_returns_nothing(self):
        result = list(inner_join(LEFT, [], on="id"))
        assert result == []

    def test_empty_left_returns_nothing(self):
        result = list(inner_join([], RIGHT, on="id"))
        assert result == []

    def test_on_key_not_duplicated_from_right(self):
        result = list(inner_join(LEFT, RIGHT, on="id"))
        for rec in result:
            assert list(rec.keys()).count("id") == 1


class TestLeftJoin:
    def test_all_left_rows_returned(self):
        result = list(left_join(LEFT, RIGHT, on="id"))
        assert len(result) == 3

    def test_matched_row_enriched(self):
        result = list(left_join(LEFT, RIGHT, on="id"))
        alice = next(r for r in result if r["name"] == "alice")
        assert alice["right_score"] == 10

    def test_unmatched_row_unchanged(self):
        result = list(left_join(LEFT, RIGHT, on="id"))
        carol = next(r for r in result if r["name"] == "carol")
        assert "right_score" not in carol

    def test_empty_right_returns_all_left(self):
        result = list(left_join(LEFT, [], on="id"))
        assert result == LEFT

    def test_empty_left_returns_nothing(self):
        result = list(left_join([], RIGHT, on="id"))
        assert result == []


class TestCrossJoin:
    def test_product_size(self):
        result = list(cross_join(LEFT, RIGHT, right_prefix="r_"))
        assert len(result) == len(LEFT) * len(RIGHT)

    def test_fields_merged(self):
        result = list(cross_join([{"x": 1}], [{"y": 2}], right_prefix="r_"))
        assert result == [{"x": 1, "r_y": 2}]

    def test_empty_right_returns_nothing(self):
        result = list(cross_join(LEFT, [], right_prefix="r_"))
        assert result == []

    def test_empty_left_returns_nothing(self):
        result = list(cross_join([], RIGHT, right_prefix="r_"))
        assert result == []
