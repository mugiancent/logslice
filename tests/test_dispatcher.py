import pytest
from logslice.dispatcher import dispatch, collect_buckets, fanout


def _collect():
    """Return a (writer, store) pair for capturing records."""
    store = []
    def writer(records):
        store.extend(records)
    return writer, store


BUCKETS = {
    "errors":   [{"level": "error", "msg": "oops"}],
    "warnings": [{"level": "warn",  "msg": "careful"}],
    "default":  [{"level": "info",  "msg": "ok"}],
}


class TestDispatch:
    def test_calls_matching_writer(self):
        writer, store = _collect()
        dispatch(BUCKETS, {"errors": writer})
        assert len(store) == 1
        assert store[0]["level"] == "error"

    def test_returns_counts_for_all_buckets(self):
        counts = dispatch(BUCKETS, {})
        assert counts == {"errors": 1, "warnings": 1, "default": 1}

    def test_default_writer_used_for_unmatched(self):
        default_writer, store = _collect()
        dispatch(BUCKETS, {}, default_writer=default_writer)
        assert len(store) == 3

    def test_explicit_writer_overrides_default(self):
        explicit, e_store = _collect()
        default, d_store = _collect()
        dispatch(BUCKETS, {"errors": explicit}, default_writer=default)
        assert len(e_store) == 1
        assert len(d_store) == 2

    def test_empty_buckets(self):
        counts = dispatch({}, {})
        assert counts == {}


class TestCollectBuckets:
    def test_returns_copy(self):
        result = collect_buckets(BUCKETS)
        assert result == BUCKETS
        assert result is not BUCKETS

    def test_inner_lists_are_copies(self):
        result = collect_buckets(BUCKETS)
        result["errors"].append({"extra": True})
        assert len(BUCKETS["errors"]) == 1


class TestFanout:
    def test_sends_to_all_writers(self):
        w1, s1 = _collect()
        w2, s2 = _collect()
        records = [{"a": 1}, {"b": 2}]
        count = fanout(records, [w1, w2])
        assert count == 2
        assert s1 == records
        assert s2 == records

    def test_empty_records(self):
        w, store = _collect()
        assert fanout([], [w]) == 0
        assert store == []
