import pytest
from logslice.renamer import rename_fields, rename_prefix, rename_suffix, apply_renames


class TestRenameFields:
    def test_renames_existing_key(self):
        result = rename_fields({"a": 1, "b": 2}, {"a": "alpha"})
        assert result == {"alpha": 1, "b": 2}

    def test_missing_source_key_ignored(self):
        result = rename_fields({"b": 2}, {"a": "alpha"})
        assert result == {"b": 2}

    def test_multiple_renames(self):
        result = rename_fields({"x": 1, "y": 2, "z": 3}, {"x": "X", "y": "Y"})
        assert result == {"X": 1, "Y": 2, "z": 3}

    def test_does_not_mutate_original(self):
        original = {"a": 1}
        rename_fields(original, {"a": "b"})
        assert "a" in original

    def test_empty_mapping_returns_copy(self):
        original = {"a": 1}
        result = rename_fields(original, {})
        assert result == original
        assert result is not original

    def test_empty_record(self):
        assert rename_fields({}, {"a": "b"}) == {}


class TestRenamePrefix:
    def test_strips_prefix(self):
        result = rename_prefix({"log_level": "info", "log_msg": "hi"}, "log_")
        assert result == {"level": "info", "msg": "hi"}

    def test_replaces_prefix(self):
        result = rename_prefix({"old_field": 1}, "old_", "new_")
        assert result == {"new_field": 1}

    def test_non_matching_keys_unchanged(self):
        result = rename_prefix({"other": 99}, "log_")
        assert result == {"other": 99}

    def test_empty_prefix_renames_all_with_replacement(self):
        result = rename_prefix({"a": 1}, "", "x_")
        assert result == {"x_a": 1}


class TestRenameSuffix:
    def test_strips_suffix(self):
        result = rename_suffix({"count_total": 5, "size_total": 3}, "_total")
        assert result == {"count": 5, "size": 3}

    def test_replaces_suffix(self):
        result = rename_suffix({"value_old": 7}, "_old", "_new")
        assert result == {"value_new": 7}

    def test_non_matching_keys_unchanged(self):
        result = rename_suffix({"name": "x"}, "_total")
        assert result == {"name": "x"}


class TestApplyRenames:
    def test_applies_to_all_records(self):
        records = [{"a": 1}, {"a": 2, "b": 3}]
        result = apply_renames(records, {"a": "alpha"})
        assert result == [{"alpha": 1}, {"alpha": 2, "b": 3}]

    def test_empty_list(self):
        assert apply_renames([], {"a": "b"}) == []
