"""Terminal colour highlighting for log fields and patterns."""

from __future__ import annotations

import re
from typing import Dict, List, Optional

ANSI_CODES: Dict[str, str] = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "bold": "\033[1m",
    "
}


def _colour(text: str, colour: str) -> str:
 = ANSI_CODES.get(colour)
    if not code:
        return text
    return f"{code}{text}{AN}"


def highlight_fields(
    record: Dict, field_colours: Dict[str, str]
) -> Dict:
    """Return a new record with string values wrapped in ANSI colour codes."""
    out = dict(record)
    for field, colour in field_colours.items():
        if field in out:
            out[field] = _colour(str(out[field]), colour)
    return out


def highlight_pattern(
    text: str, pattern: str, colour: str = "yellow"
) -> str:
    """Wrap all occurrences of *pattern* in *text* with ANSI colour codes."""
    code = ANSI_CODES.get(colour, ANSI_CODES["yellow"])
    reset = ANSI_CODES["reset"]

    def replacer(m: re.Match) -> str:
        return f"{code}{m.group(0)}{reset}"

    return re.sub(pattern, replacer, text)


def apply_highlights(
    records: List[Dict],
    field_colours: Optional[Dict[str, str]] = None,
    pattern: Optional[str] = None,
    pattern_colour: str = "yellow",
) -> List[Dict]:
    """Apply field and/or pattern highlights to a list of records."""
    result = []
    for record in records:
        r = highlight_fields(record, field_colours or {})
        if pattern:
            r = {
                k: highlight_pattern(str(v), pattern, pattern_colour)
                for k, v in r.items()
            }
        result.append(r)
    return result
