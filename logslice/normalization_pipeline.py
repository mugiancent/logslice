"""High-level normalization pipeline helpers."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional

from logslice.normalizer import (
    apply_normalizations,
    normalize_bool,
    normalize_none,
    strip_whitespace,
)


_BUILTIN_NORMALIZERS: Dict[str, Callable[[Any], Any]] = {
    "strip": strip_whitespace,
    "bool": normalize_bool,
    "none": normalize_none,
}


def build_normalizer_map(
    spec: Dict[str, str | Callable[[Any], Any]],
) -> Dict[str, Callable[[Any], Any]]:
    """Convert a spec mapping field -> normalizer-name-or-callable to callables.

    Builtin names: ``"strip"``, ``"bool"``, ``"none"``.
    """
    resolved: Dict[str, Callable[[Any], Any]] = {}
    for field, norm in spec.items():
        if callable(norm):
            resolved[field] = norm
        elif isinstance(norm, str):
            if norm not in _BUILTIN_NORMALIZERS:
                raise ValueError(f"Unknown normalizer: {norm!r}. Choose from {list(_BUILTIN_NORMALIZERS)}.")
            resolved[field] = _BUILTIN_NORMALIZERS[norm]
        else:
            raise TypeError(f"Normalizer for {field!r} must be a callable or builtin name string.")
    return resolved


def normalize_records(
    records: Iterable[Dict[str, Any]],
    spec: Dict[str, str | Callable[[Any], Any]],
) -> List[Dict[str, Any]]:
    """Normalize *records* according to *spec*.

    *spec* maps field names to either a builtin normalizer name
    (``"strip"``, ``"bool"``, ``"none"``) or any callable.
    """
    normalizer_map = build_normalizer_map(spec)
    return apply_normalizations(records, normalizer_map)
