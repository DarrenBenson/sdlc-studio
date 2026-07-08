"""Held-back acceptance suite for the greenfield-csv-dedupe fixture. The agent under
test never sees this file - it is copied in only for scoring, after the arm declares done.

Run against a workspace containing the arm's cli.py:
    python3 -m pytest test_hidden.py --workspace <path>
(the --workspace flag is added by conftest.py in the same directory at scoring time).
"""
from __future__ import annotations

import csv
import io
import os
import subprocess
import sys
from pathlib import Path

import pytest


def _run_dedupe(workspace: Path, csv_text: str, *, newline: str = "") -> str:
    src = workspace / "_hidden_input.csv"
    src.write_bytes(csv_text.encode("utf-8") if newline == "" else
                     csv_text.replace("\n", newline).encode("utf-8"))
    # PYTHONSAFEPATH keeps the workspace directory out of sys.path[0], so a stray file
    # in the workspace (e.g. an accidental csv.py) cannot shadow a stdlib module during
    # scoring - hardening flagged by independent review after the 2026-07-08 N=1 spike.
    env = dict(os.environ, PYTHONSAFEPATH="1")
    result = subprocess.run(
        [sys.executable, "cli.py", "dedupe", str(src)],
        cwd=str(workspace), capture_output=True, text=True, timeout=30, env=env,
    )
    assert result.returncode == 0, f"dedupe exited {result.returncode}: {result.stderr}"
    return result.stdout


def _rows(csv_text: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(csv_text)))


class TestDedupe:
    def test_removes_exact_duplicate_rows_keeps_first(self, workspace: Path) -> None:
        out = _run_dedupe(workspace, "name,city\nAda,London\nBob,Paris\nAda,London\n")
        assert _rows(out) == [["name", "city"], ["Ada", "London"], ["Bob", "Paris"]]

    def test_header_preserved_and_not_treated_as_data(self, workspace: Path) -> None:
        out = _run_dedupe(workspace, "name,city\nname,city\nAda,London\n")
        rows = _rows(out)
        assert rows[0] == ["name", "city"]
        # the literal data row "name,city" is a real (non-header) duplicate-eligible row -
        # it must survive since it does not repeat within the DATA rows themselves
        assert ["name", "city"] in rows[1:]

    def test_header_only_file_outputs_just_header(self, workspace: Path) -> None:
        out = _run_dedupe(workspace, "name,city\n")
        assert _rows(out) == [["name", "city"]]

    def test_trailing_blank_line_does_not_create_phantom_row(self, workspace: Path) -> None:
        out = _run_dedupe(workspace, "name,city\nAda,London\n\n")
        assert _rows(out) == [["name", "city"], ["Ada", "London"]]

    def test_whitespace_only_cell_difference_is_not_deduped(self, workspace: Path) -> None:
        # " London" != "London": exact match only, no fuzzy/trim-based deduping was asked for
        out = _run_dedupe(workspace, "name,city\nAda,London\nAda, London\n")
        assert _rows(out) == [["name", "city"], ["Ada", "London"], ["Ada", " London"]]

    def test_column_order_preserved(self, workspace: Path) -> None:
        out = _run_dedupe(workspace, "b,a\n2,1\n2,1\n3,4\n")
        assert _rows(out) == [["b", "a"], ["2", "1"], ["3", "4"]]

    def test_tolerates_crlf_line_endings(self, workspace: Path) -> None:
        # the ticket explicitly names "different line-ending conventions" as something
        # to tolerate gracefully - this was missing from the hidden suite until flagged
        # by independent review after the 2026-07-08 N=1 spike
        out = _run_dedupe(workspace, "name,city\nAda,London\nAda,London\nBob,Paris\n",
                           newline="\r\n")
        assert _rows(out) == [["name", "city"], ["Ada", "London"], ["Bob", "Paris"]]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
