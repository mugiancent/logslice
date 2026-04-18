"""Schema definition helpers for building reusable validation rule sets."""
from typing import Any, Callable, Dict, List, Optional
from logslice.validator import (
    ValidationError,
    require_fields,
    require_type,
    require_pattern,
    apply_validations,
)


FieldSpec = Dict[str, Any]


class Schema:
    """Declarative schema that compiles to a list of validation rules."""

    def __init__(self, fields: List[FieldSpec]):
        """
        Each FieldSpec may contain:
          name (str, required)
          required (bool, default False)
          type (type, optional)
          pattern (str, optional)
        """
        self._fields = fields
        self._rules = self._compile(fields)

    def _compile(self, fields: List[FieldSpec]) -> List[Callable]:
        rules: List[Callable] = []
        required_names = [f["name"] for f in fields if f.get("required")]
        if required_names:
            rules.append(lambda r, names=required_names: require_fields(r, names))
        for spec in fields:
            name = spec["name"]
            if "type" in spec:
                rules.append(lambda r, n=name, t=spec["type"]: require_type(r, n, t))
            if "pattern" in spec:
                rules.append(lambda r, n=name, p=spec["pattern"]: require_pattern(r, n, p))
        return rules

    def validate(self, record: Dict[str, Any]) -> List[ValidationError]:
        """Return list of validation errors for record."""
        return apply_validations(record, self._rules)

    def is_valid(self, record: Dict[str, Any]) -> bool:
        return len(self.validate(record)) == 0

    @classmethod
    def from_dict(cls, spec: Dict[str, Any]) -> "Schema":
        """Build Schema from a plain dict, e.g. loaded from JSON/YAML."""
        return cls(spec.get("fields", []))
