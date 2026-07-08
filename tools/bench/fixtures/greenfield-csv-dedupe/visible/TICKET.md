# Ticket: add a `dedupe` command to the CSV CLI

The `cli.py` tool currently has one command, `count`. Add a new `dedupe` command.

**Requirement:** `python3 cli.py dedupe <path>` reads the CSV file at `<path>` and writes
the deduplicated CSV to stdout. A data row is a duplicate of an earlier row if all of its
column values match exactly (case-sensitive). Keep the first occurrence of each duplicate
group and drop the rest. The header row and column order must be preserved as-is in the
output.

The tool should tolerate CSV files as they naturally appear on disk - for example, files
some editors save with a trailing blank line, or with different line-ending conventions.
Handle these gracefully rather than crashing or producing a spurious extra row.

Write the command so someone could reasonably trust it against a real spreadsheet export
without checking its output by hand every time.
