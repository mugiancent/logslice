"""Tests for logslice.windower."""

import pytest
from logslice.windower import tumbling_windows, sliding_windows, window_counts


def rec(ts: float, **kw) -> dict:
    return {"timestamp": ts, **kw}


# ---------------------------------------------------------------------------
# tumbling_windows
# ---------------------------------------------------------------------------

class TestTumblingWindows:
    def test_single_window(self):
        records = [rec(0), rec(1), rec(2)]
        result = list(tumbling_windows(records, width=10))
        assert len(result) == 1
        assert result[0][0] == 0
        assert len(result[0][1]) == 3

    def test_two_windows(self):
        records = [rec(0), rec(1), rec(10), rec(11)]
        result = list(tumbling_windows(records, width=10))
        assert len(result) == 2
        starts = [r[0] for r in result]
        assert starts[0] == 0
        assert starts[1] == 10

    def test_empty_input_yields_nothing(self):
        result = list(tumbling_windows([], width=5))
        assert result == []

    def test_invalid_width_raises(self):
        with pytest.raises(ValueError):
            list(tumbling_windows([rec(0)], width=0))

    def test_custom_ts_field(self):
        records = [{"t": 0}, {"t": 5}, {"t": 15}]
        result = list(tumbling_windows(records, width=10, ts_field="t"))
        assert len(result) == 2

    def test_missing_ts_field_treated_as_zero(self):
        records = [{"msg": "a"}, {"msg": "b"}]
        result = list(tumbling_windows(records, width=5))
        assert len(result) == 1
        assert len(result[0][1]) == 2

    def test_single_record(self):
        result = list(tumbling_windows([rec(42)], width=10))
        assert len(result) == 1
        assert result[0][0] == 42


# ---------------------------------------------------------------------------
# sliding_windows
# ---------------------------------------------------------------------------

class TestSlidingWindows:
    def test_overlapping_windows(self):
        records = [rec(i) for i in range(5)]
        result = list(sliding_windows(records, width=3, step=1))
        # windows start at 0,1,2,3,4
        assert len(result) == 5

    def test_empty_input(self):
        assert list(sliding_windows([], width=5, step=1)) == []

    def test_step_equals_width_is_tumbling(self):
        records = [rec(0), rec(1), rec(5), rec(6)]
        tumbling = list(tumbling_windows(records, width=5))
        sliding = list(sliding_windows(records, width=5, step=5))
        assert len(tumbling) == len(sliding)

    def test_invalid_width_raises(self):
        with pytest.raises(ValueError):
            list(sliding_windows([rec(0)], width=0, step=1))

    def test_step_greater_than_width_raises(self):
        with pytest.raises(ValueError):
            list(sliding_windows([rec(0)], width=2, step=5))

    def test_records_appear_in_multiple_windows(self):
        records = [rec(0), rec(1), rec(2)]
        result = list(sliding_windows(records, width=3, step=1))
        total = sum(len(b) for _, b in result)
        assert total > len(records)  # overlap means records counted multiple times


# ---------------------------------------------------------------------------
# window_counts
# ---------------------------------------------------------------------------

class TestWindowCounts:
    def test_counts_match_bucket_sizes(self):
        windows = [(0.0, [rec(0), rec(1)]), (10.0, [rec(10)])]
        counts = window_counts(iter(windows))
        assert counts == {0.0: 2, 10.0: 1}

    def test_empty_yields_empty_dict(self):
        assert window_counts(iter([])) == {}
