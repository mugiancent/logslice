"""Tests for logslice.sampler."""
import pytest
from logslice.sampler import sample_every_nth, sample_by_rate, sample_reservoir

RECORDS = [{"id": str(i), "level": "info"} for i in range(10)]


class TestSampleEveryNth:
    def test_n1_returns_all(self):
        result = list(sample_every_nth(RECORDS, 1))
        assert result == RECORDS

    def test_n2_returns_half(self):
        result = list(sample_every_nth(RECORDS, 2))
        assert len(result) == 5
        assert result[0] == RECORDS[0]
        assert result[1] == RECORDS[2]

    def test_n_larger_than_records(self):
        result = list(sample_every_nth(RECORDS, 100))
        assert result == [RECORDS[0]]

    def test_invalid_n_raises(self):
        with pytest.raises(ValueError):
            list(sample_every_nth(RECORDS, 0))

    def test_empty_input(self):
        assert list(sample_every_nth([], 3)) == []


class TestSampleByRate:
    def test_rate_zero_returns_none(self):
        result = list(sample_by_rate(RECORDS, 0.0))
        assert result == []

    def test_rate_one_returns_all(self):
        result = list(sample_by_rate(RECORDS, 1.0))
        assert result == RECORDS

    def test_invalid_rate_raises(self):
        with pytest.raises(ValueError):
            list(sample_by_rate(RECORDS, 1.5))

    def test_invalid_negative_rate_raises(self):
        with pytest.raises(ValueError):
            list(sample_by_rate(RECORDS, -0.1))

    def test_partial_rate_subset(self):
        result = list(sample_by_rate(RECORDS, 0.5))
        assert 0 <= len(result) <= len(RECORDS)


class TestSampleReservoir:
    def test_returns_k_records_when_enough(self):
        result = sample_reservoir(RECORDS, 3)
        assert len(result) == 3

    def test_returns_all_when_k_exceeds_input(self):
        result = sample_reservoir(RECORDS, 100)
        assert len(result) == len(RECORDS)

    def test_k_zero_returns_empty(self):
        result = sample_reservoir(RECORDS, 0)
        assert result == []

    def test_invalid_k_raises(self):
        with pytest.raises(ValueError):
            sample_reservoir(RECORDS, -1)

    def test_empty_input(self):
        assert sample_reservoir([], 5) == []

    def test_result_is_subset_of_input(self):
        """All records returned by reservoir sampling must come from the input."""
        result = sample_reservoir(RECORDS, 5)
        for record in result:
            assert record in RECORDS

    def test_no_duplicates(self):
        """Reservoir sampling should not return duplicate records."""
        result = sample_reservoir(RECORDS, len(RECORDS))
        seen_ids = [r["id"] for r in result]
        assert len(seen_ids) == len(set(seen_ids))
