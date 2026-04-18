"""Structured log line parser supporting JSON and logfmt formats."""

import json
from typing import Optional


def parse_line(line: str) -> Optional[dict]:
    """Parse a single log line into a dictionary.

    Supports JSON and logfmt formats. Returns None if parsing fails.
    """
    line = line.strip()
    if not line:
        return None

    # Try JSON first
    if line.startswith("{"):
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            pass

    # Try logfmt (key=value key="value with spaces")
    return _parse_logfmt(line)


def _parse_logfmt(line: str) -> Optional[dict]:
    """Parse a logfmt-encoded log line."""
    result = {}
    i = 0
    n = len(line)

    while i < n:
        # Skip whitespace
        while i < n and line[i] == " ":
            i += 1
        if i >= n:
            break

        # Read key
        key_start = i
        while i < n and line[i] not in ("=", " "):
            i += 1
        key = line[key_start:i]
        if not key:
            return None

        if i >= n or line[i] != "=":
            result[key] = True
            continue
        i += 1  # skip '='

        # Read value
        if i < n and line[i] == '"':
            i += 1
            value_start = i
            while i < n and line[i] != '"':
                i += 1
            value = line[value_start:i]
            if i < n:
                i += 1  # skip closing quote
        else:
            value_start = i
            while i < n and line[i] != " ":
                i += 1
            value = line[value_start:i]

        result[key] = value

    return result if result else None
