import pytest
from logslice.flattener import flatten_record, flatten_records, unflatten_record


class TestFlattenRecord:
    def test_already_flat(self):
        r = {"a": 1, "b": "x"}
        assert flatten_record(r) == {"a": 1, "b": "x"}

    def test_one_level_nested(self):
        r = {"a": {"b": 1, "c": 2}}
        assert flatten_record(r) == {"a.b": 1, "a.c": 2}

    def test_two_levels_nested(self):
        r = {"a": {"b": {"c": 42}}}
        assert flatten_record(r) == {"a.b.c": 42}

    def test_mixed_flat_and_nested(self):
        r = {"ts": "2024-01-01", "meta": {"host": "web1", "env": "prod"}}
        result = flatten_record(r)
        assert result["ts"] == "2024-01-01"
        assert result["meta.host"] == "web1"
        assert result["meta.env"] == "prod"

    def test_custom_separator(self):
        r = {"a": {"b": 1}}
        assert flatten_record(r, sep="_") == {"a_b": 1}

    def test_does_not_mutate_original(self):
        r = {"a": {"b": 1}}
        flatten_record(r)
        assert r == {"a": {"b": 1}}

    def test_max_depth_zero_returns_as_is(self):
        r = {"a": {"b": 1}}
        result = flatten_record(r, max_depth=0)
        assert result == {"a": {"b": 1}}

    def test_max_depth_one(self):
        r = {"a": {"b": {"c": 1}}}
        result = flatten_record(r, max_depth=1)
        assert "a.b" in result
        assert isinstance(result["a.b"], dict)

    def test_empty_record(self):
        assert flatten_record({}) == {}

    def test_non_dict_value_unchanged(self):
        r = {"tags": ["a", "b"]}
        assert flatten_record(r) == {"tags": ["a", "b"]}


class TestFlattenRecords:
    def test_flattens_all(self):
        records = [{"a": {"b": i}} for i in range(3)]
        result = flatten_records(records)
        assert all("a.b" in r for r in result)

    def test_empty_list(self):
        assert flatten_records([]) == []


class TestUnflattenRecord:
    def test_simple(self):
        r = {"a.b": 1, "a.c": 2}
        assert unflatten_record(r) == {"a": {"b": 1, "c": 2}}

    def test_deep(self):
        r = {"a.b.c": 42}
        assert unflatten_record(r) == {"a": {"b": {"c": 42}}}

    def test_flat_key_unchanged(self):
        r = {"level": "info"}
        assert unflatten_record(r) == {"level": "info"}

    def test_roundtrip(self):
        original = {"meta": {"host": "web1", "region": "us-east"}}
        assert unflatten_record(flatten_record(original)) == original
