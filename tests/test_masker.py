"""Tests for logslice.masker."""
import pytest
from logslice.masker import apply_masks, mask_field, mask_pattern


class TestMaskField:
    def test_middle_chars_masked(self):
        r = mask_field({"card": "1234567890"}, "card", keep_start=2, keep_end=3)
        assert r["card"] == "12*****890"

    def test_keep_end_only(self):
        r = mask_field({"token": "abcdef"}, "token", keep_end=2)
        assert r["token"] == "****ef"

    def test_keep_start_only(self):
        r = mask_field({"token": "abcdef"}, "token", keep_start=2)
        assert r["token"] == "ab****"

    def test_custom_mask_char(self):
        r = mask_field({"pin": "12345"}, "pin", keep_end=1, mask_char="#")
        assert r["pin"] == "####5"

    def test_short_value_returned_unchanged(self):
        r = mask_field({"v": "hi"}, "v", keep_start=1, keep_end=1)
        assert r["v"] == "hi"

    def test_missing_field_returns_unchanged(self):
        r = mask_field({"a": "x"}, "missing", keep_end=2)
        assert r == {"a": "x"}

    def test_non_string_value_unchanged(self):
        r = mask_field({"age": 42}, "age", keep_end=1)
        assert r["age"] == 42

    def test_does_not_mutate_original(self):
        original = {"secret": "password123"}
        mask_field(original, "secret", keep_end=3)
        assert original["secret"] == "password123"

    def test_other_fields_preserved(self):
        r = mask_field({"a": "hello", "b": 1}, "a", keep_start=1)
        assert r["b"] == 1


class TestMaskPattern:
    def test_replaces_matching_pattern(self):
        r = mask_pattern({"msg": "call 555-1234 now"}, "msg", r"\d{3}-\d{4}", "***-****")
        assert r["msg"] == "call ***-**** now"

    def test_no_match_leaves_value_unchanged(self):
        r = mask_pattern({"msg": "hello world"}, "msg", r"\d+")
        assert r["msg"] == "hello world"

    def test_missing_field_returns_unchanged(self):
        r = mask_pattern({"a": "x"}, "missing", r"\d+")
        assert r == {"a": "x"}

    def test_non_string_unchanged(self):
        r = mask_pattern({"n": 123}, "n", r"\d+")
        assert r["n"] == 123

    def test_does_not_mutate_original(self):
        original = {"email": "user@example.com"}
        mask_pattern(original, "email", r"@.*", "@***")
        assert original["email"] == "user@example.com"


class TestApplyMasks:
    def test_applies_field_specs(self):
        records = [{"card": "9999000011112222"}]
        result = apply_masks(records, field_specs=[{"field": "card", "keep_end": 4}])
        assert result[0]["card"].endswith("2222")
        assert "*" in result[0]["card"]

    def test_applies_pattern_specs(self):
        records = [{"log": "ip=192.168.1.1 status=200"}]
        result = apply_masks(
            records,
            pattern_specs=[{"field": "log", "pattern": r"\d+\.\d+\.\d+\.\d+", "replacement": "x.x.x.x"}],
        )
        assert result[0]["log"] == "ip=x.x.x.x status=200"

    def test_empty_specs_returns_copies(self):
        records = [{"a": "hello"}]
        result = apply_masks(records)
        assert result == records
        assert result[0] is not records[0]

    def test_multiple_records_all_masked(self):
        records = [{"pw": "secret1"}, {"pw": "secret2"}]
        result = apply_masks(records, field_specs=[{"field": "pw", "keep_end": 1}])
        assert result[0]["pw"].endswith("1")
        assert result[1]["pw"].endswith("2")
