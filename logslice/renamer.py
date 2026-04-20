"""Bulk field renaming utilities."""
from typing import Dict, List


def rename_fields(record: dict, mapping: Dict[str, str]) -> dict:
    """Return a new record with fields renamed according to *mapping*.

    Keys not present in *mapping* are left untouched.  If a source key does
    not exist in the record it is silently ignored.
    """
    out = {}
    for k, v in record.items():
        out[mapping.get(k, k)] = v
    return out


def rename_prefix(record: dict, prefix: str, replacement: str = "") -> dict:
    """Strip or replace a common prefix from every matching field name."""
    out = {}
    for k, v in record.items():
        if k.startswith(prefix):
            new_key = replacement + k[len(prefix):]
            out[new_key] = v
        else:
            out[k] = v
    return out


def rename_suffix(record: dict, suffix: str, replacement: str = "") -> dict:
    """Strip or replace a common suffix from every matching field name."""
    out = {}
    for k, v in record.items():
        if k.endswith(suffix):
            new_key = k[: len(k) - len(suffix)] + replacement
            out[new_key] = v
        else:
            out[k] = v
    return out


def apply_renames(records: List[dict], mapping: Dict[str, str]) -> List[dict]:
    """Apply :func:`rename_fields` to every record in *records*."""
    return [rename_fields(r, mapping) for r in records]
