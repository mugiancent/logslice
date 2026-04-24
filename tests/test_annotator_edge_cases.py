"""Edge-case tests for logslice.annotator."""
import pytest
from logslice.annotator import (
    annotate_with_index,
    annotate_with_flag,
    annotate_with_match,
    apply_annotations,
)


class TestAnnotateWithIndexEdgeCases:
    def test_single_record(self):
        result = annotate_with_index([{"a": 1}])
        assert result[0]["_index"] == 0

    def test_negative_start(self):
        result = annotate_with_index([{"a": 1}, {"b": 2}], start=-1)
        assert result[0]["_index"] == -1
        assert result[1]["_index"] == 0

    def test_existing_field_overwritten(self):
        records = [{"_index": 99, "x": 1}]
        result = annotate_with_index(records)
        assert result[0]["_index"] == 0

    def test_other_fields_preserved(self):
        records = [{"level": "info", "msg": "hi"}]
        result = annotate_with_index(records)
        assert result[0]["level"] == "info"
        assert result[0]["msg"] == "hi"


class TestAnnotateWithFlagEdgeCases:
    def test_predicate_exception_propagates(self):
        def bad(r):
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            annotate_with_flag([{"x": 1}], bad)

    def test_all_true(self):
        records = [{"a": 1}, {"a": 2}]
        result = annotate_with_flag(records, lambda r: True)
        assert all(r["_flagged"] for r in result)

    def test_all_false(self):
        records = [{"a": 1}, {"a": 2}]
        result = annotate_with_flag(records, lambda r: False)
        assert not any(r["_flagged"] for r in result)


class TestAnnotateWithMatchEdgeCases:
    def test_numeric_field_value_coerced_to_str(self):
        records = [{"code": 404}]
        result = annotate_with_match(records, "code", r"\d+")
        assert result[0]["_match"] == "404"

    def test_only_first_match_captured(self):
        records = [{"msg": "a1 b2 c3"}]
        result = annotate_with_match(records, "msg", r"\d+")
        assert result[0]["_match"] == "1"

    def test_custom_dest_field(self):
        records = [{"msg": "err 500"}]
        result = annotate_with_match(records, "msg", r"\d+", dest_field="code")
        assert "code" in result[0]
        assert "_match" not in result[0]


class TestApplyAnnotationsEdgeCases:
    def test_single_annotation(self):
        import functools
        fn = functools.partial(annotate_with_index, field="n")
        result = apply_annotations([{"x": 1}], [fn])
        assert result[0]["n"] == 0

    def test_annotations_applied_sequentially(self):
        """Second annotation sees fields added by first."""
        import functools
        fn1 = functools.partial(annotate_with_index, field="_index")
        fn2 = functools.partial(
            annotate_with_flag,
            predicate=lambda r: r.get("_index", -1) == 0,
            field="_first",
        )
        result = apply_annotations([{"a": 1}, {"a": 2}], [fn1, fn2])
        assert result[0]["_first"] is True
        assert result[1]["_first"] is False
