import pytest
from logslice.router import make_predicate, make_regex_predicate, route_records


RECORDS = [
    {"level": "error", "msg": "disk full"},
    {"level": "warn",  "msg": "low memory"},
    {"level": "info",  "msg": "started"},
    {"level": "error", "msg": "timeout"},
    {"level": "debug", "msg": "loop tick"},
]


class TestMakePredicate:
    def test_matches_equal_value(self):
        pred = make_predicate("level", "error")
        assert pred({"level": "error"}) is True

    def test_no_match_different_value(self):
        pred = make_predicate("level", "error")
        assert pred({"level": "info"}) is False

    def test_missing_field_no_match(self):
        pred = make_predicate("level", "error")
        assert pred({"msg": "hi"}) is False


class TestMakeRegexPredicate:
    def test_matches_pattern(self):
        pred = make_regex_predicate("msg", r"time")
        assert pred({"msg": "timeout"}) is True

    def test_no_match(self):
        pred = make_regex_predicate("msg", r"^error")
        assert pred({"msg": "timeout"}) is False

    def test_missing_field_treated_as_empty(self):
        pred = make_regex_predicate("msg", r"^$")
        assert pred({}) is True


class TestRouteRecords:
    def _routes(self):
        return [
            ("errors", make_predicate("level", "error")),
            ("warnings", make_predicate("level", "warn")),
        ]

    def test_routes_to_correct_buckets(self):
        buckets = route_records(RECORDS, self._routes())
        assert len(buckets["errors"]) == 2
        assert len(buckets["warnings"]) == 1

    def test_unmatched_go_to_default(self):
        buckets = route_records(RECORDS, self._routes())
        assert len(buckets["default"]) == 2

    def test_custom_default_name(self):
        buckets = route_records(RECORDS, self._routes(), default="other")
        assert "other" in buckets
        assert len(buckets["other"]) == 2

    def test_empty_records(self):
        buckets = route_records([], self._routes())
        assert buckets["errors"] == []
        assert buckets["default"] == []

    def test_no_routes_all_default(self):
        buckets = route_records(RECORDS, [])
        assert len(buckets["default"]) == len(RECORDS)

    def test_first_matching_route_wins(self):
        routes = [
            ("first", make_predicate("level", "error")),
            ("second", make_predicate("level", "error")),
        ]
        buckets = route_records(RECORDS, routes)
        assert len(buckets["first"]) == 2
        assert len(buckets["second"]) == 0
