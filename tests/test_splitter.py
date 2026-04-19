import pytest
from logslice.splitter import split_by_field, split_by_predicate, split_by_value, split_chunks

RECORDS = [
    {"level": "info", "msg": "a"},
    {"level": "error", "msg": "b"},
    {"level": "info", "msg": "c"},
    {"msg": "d"},  # missing 'level'
    {"level": "warn", "msg": "e"},
]


class TestSplitByField:
    def test_groups_correctly(self):
        result = split_by_field(RECORDS, "level")
        assert len(result["info"]) == 2
        assert len(result["error"]) == 1
        assert len(result["warn"]) == 1

    def test_missing_field_goes_to_empty_key(self):
        result = split_by_field(RECORDS, "level")
        assert result[""] == [{"msg": "d"}]

    def test_empty_records(self):
        assert split_by_field([], "level") == {}

    def test_all_same_value(self):
        recs = [{"k": "x"}, {"k": "x"}]
        result = split_by_field(recs, "k")
        assert list(result.keys()) == ["x"]
        assert len(result["x"]) == 2


class TestSplitByPredicate:
    def test_splits_correctly(self):
        matched, unmatched = split_by_predicate(RECORDS, lambda r: r.get("level") == "error")
        assert len(matched) == 1
        assert matched[0]["msg"] == "b"
        assert len(unmatched) == 4

    def test_all_match(self):
        matched, unmatched = split_by_predicate(RECORDS, lambda r: True)
        assert len(matched) == len(RECORDS)
        assert unmatched == []

    def test_none_match(self):
        matched, unmatched = split_by_predicate(RECORDS, lambda r: False)
        assert matched == []
        assert len(unmatched) == len(RECORDS)


class TestSplitByValue:
    def test_in_values(self):
        matched, unmatched = split_by_value(RECORDS, "level", ["info", "warn"])
        assert len(matched) == 3
        assert all(r["level"] in ("info", "warn") for r in matched)

    def test_empty_values(self):
        matched, unmatched = split_by_value(RECORDS, "level", [])
        assert matched == []
        assert len(unmatched) == len(RECORDS)


class TestSplitChunks:
    def test_even_split(self):
        recs = [{"i": i} for i in range(6)]
        chunks = split_chunks(recs, 2)
        assert len(chunks) == 3
        assert all(len(c) == 2 for c in chunks)

    def test_last_chunk_partial(self):
        recs = [{"i": i} for i in range(5)]
        chunks = split_chunks(recs, 3)
        assert len(chunks) == 2
        assert len(chunks[-1]) == 2

    def test_empty_input(self):
        assert split_chunks([], 3) == []

    def test_invalid_size_raises(self):
        with pytest.raises(ValueError):
            split_chunks([{"a": 1}], 0)
