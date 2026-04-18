"""Command-line interface for logslice."""
import argparse
import sys
from typing import List, Optional

from logslice.parser import parse_line
from logslice.filter import filter_by_time, filter_by_field
from logslice.output import write_records


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logslice",
        description="Filter and slice structured log files by time range or field value.",
    )
    p.add_argument("file", nargs="?", help="Log file to read (default: stdin)")
    p.add_argument("--start", metavar="TIMESTAMP", help="Include records at or after this timestamp")
    p.add_argument("--end", metavar="TIMESTAMP", help="Include records at or before this timestamp")
    p.add_argument(
        "--field",
        metavar="KEY=VALUE",
        action="append",
        dest="fields",
        default=[],
        help="Filter by field value (repeatable)",
    )
    p.add_argument(
        "--format",
        choices=["json", "logfmt", "pretty"],
        default="json",
        help="Output format (default: json)",
    )
    p.add_argument("--quiet", action="store_true", help="Suppress count summary on stderr")
    return p


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.file:
        try:
            stream = open(args.file, "r")
        except OSError as exc:
            print(f"logslice: error opening file: {exc}", file=sys.stderr)
            return 1
    else:
        stream = sys.stdin

    try:
        records = []
        for line in stream:
            record = parse_line(line)
            if record is not None:
                records.append(record)

        records = list(filter_by_time(records, start=args.start, end=args.end))

        for field_expr in args.fields:
            if "=" not in field_expr:
                print(f"logslice: invalid --field expression: {field_expr!r}", file=sys.stderr)
                return 1
            key, value = field_expr.split("=", 1)
            records = list(filter_by_field(records, key, value))

        count = write_records(records, fmt=args.format)

        if not args.quiet:
            print(f"# {count} record(s) matched.", file=sys.stderr)
    finally:
        if args.file:
            stream.close()

    return 0


def main():
    sys.exit(run())


if __name__ == "__main__":
    main()
