# logslice

A CLI tool to filter and slice structured log files by time range or field value.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/yourname/logslice.git && cd logslice && pip install .
```

---

## Usage

```bash
# Filter logs by time range
logslice --file app.log --start "2024-01-15T08:00:00" --end "2024-01-15T09:00:00"

# Filter by field value
logslice --file app.log --field level=ERROR

# Combine filters and output to file
logslice --file app.log --start "2024-01-15T08:00:00" --field service=api -o filtered.log
```

### Options

| Flag | Description |
|------|-------------|
| `--file` | Path to the structured log file (JSON, NDJSON) |
| `--start` | Start of time range (ISO 8601) |
| `--end` | End of time range (ISO 8601) |
| `--field` | Filter by field value in `key=value` format |
| `-o` | Output file (defaults to stdout) |

---

## Example

```bash
$ logslice --file server.log --field level=ERROR --start "2024-01-15T00:00:00"
{"timestamp": "2024-01-15T03:22:11", "level": "ERROR", "message": "Connection timeout"}
{"timestamp": "2024-01-15T07:45:03", "level": "ERROR", "message": "Disk quota exceeded"}
```

---

## License

MIT © 2024 yourname