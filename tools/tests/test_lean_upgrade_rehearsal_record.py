"""US0962: the migration to v6 is rehearsed on two real consuming projects, and the record says so.

`docs/upgrade-rehearsal-v6.md` is the one-off record the 6.0.0 notes link. It names each project
by the version it recorded, never by name, and carries one row per project with both `migrate`
commands and their exit codes, what `--apply` changed and what it left to a human, and the
`validate.py check` and `gate.py` exit codes either side. Every finding it reports has an owner
that resolves in this workspace, so the notes never have to disclose an unowned failure by hand.

The criteria name this repository's record, so the tests read it; nothing here writes the tree.
"""
# test-census-subject: docs/upgrade-rehearsal-v6.md
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RECORD = REPO / "docs" / "upgrade-rehearsal-v6.md"
sys.path.insert(0, str(REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"))

from lib import sdlc_md  # noqa: E402
import decisions  # noqa: E402

#: The two projects the criterion names, by the skill version each recorded before the upgrade.
RECORDED = {"4.1.0", "2.4.1"}
EXIT = re.compile(r"\bexit\s+(\d+)\b")
OWNER = re.compile(r"\b(BG\d{4}|CR\d{4}|D\d{4})\b")


def _table(text: str, heading: str) -> list[dict]:
    """The rows of the first table under `## <heading>`, as {column: cell}; [] when absent."""
    section = re.search(rf"(?ms)^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text)
    if not section:
        return []
    lines = [ln.strip() for ln in section.group(1).splitlines() if ln.strip().startswith("|")]
    if len(lines) < 2:
        return []

    def cells(line: str) -> list[str]:
        return [c.strip() for c in line.strip("|").split("|")]

    header = cells(lines[0])
    return [dict(zip(header, cells(ln))) for ln in lines[2:]]


def _column(row: dict, *words: str) -> str:
    """The cell whose header holds every word (case-insensitive); fails loudly when none does."""
    for key, value in row.items():
        if all(w.lower() in key.lower() for w in words):
            return value
    raise AssertionError(f"the record's table has no column naming {words}: {sorted(row)}")


class UpgradeRehearsalRecordTests(unittest.TestCase):

    def setUp(self) -> None:
        self.assertTrue(RECORD.is_file(), f"{RECORD} is missing")
        self.text = RECORD.read_text(encoding="utf-8")

    def test_each_project_row_records_both_commands_and_their_exit_codes(self) -> None:
        """AC1. MUTANTS: (1) a record written from the dry run alone (no `--apply` exit, the
        version after equal to the version before, nothing applied); (2) a row labelled by a
        name rather than its recorded version; (3) one project's row dropped; (4) the validate
        or gate cell carrying only the before exit code."""
        rows = _table(self.text, "Projects")
        self.assertEqual(len(rows), 2, "one row per rehearsed project")
        before = set()
        for row in rows:
            was = _column(row, "version", "before")
            after = _column(row, "version", "after")
            before.add(was)
            label = next(iter(row.values()))
            major_minor = ".".join(was.split(".")[:2])
            self.assertRegex(label, rf"^a v{re.escape(major_minor)} project\b",
                             "a row is labelled by its recorded version, never by name")
            self.assertNotEqual(after, was, f"{label}: the version did not move - a dry run only")
            self.assertTrue(after.startswith("6.0.0"), f"{label}: after is {after!r}")
            self.assertRegex(_column(row, "migrate", "dry"), EXIT, f"{label}: dry-run exit")
            self.assertRegex(_column(row, "--apply"), EXIT, f"{label}: --apply exit")
            for cell in ("applied", "left to a human"):
                value = _column(row, cell)
                self.assertNotIn(value.lower(), {"", "-", "none", "n/a"}, f"{label}: {cell}")
            for tool in ("validate", "gate"):
                self.assertEqual(len(EXIT.findall(_column(row, tool))), 2,
                                 f"{label}: `{tool}` needs its exit code before AND after")
        self.assertEqual(before, RECORDED)

    def test_every_finding_row_names_an_owner_that_resolves(self) -> None:
        """AC2. MUTANTS: (1) a finding row with no id (prose only); (2) an id that resolves to
        nothing in this workspace (an unsubstituted placeholder, a typo); (3) the Findings table
        removed, so no row is judged."""
        rows = _table(self.text, "Findings")
        self.assertTrue(rows, "the record carries a Findings table with at least one row")
        decided = {d["id"] for d in decisions.list_decisions(REPO)}
        for row in rows:
            owner = _column(row, "owner")
            ids = OWNER.findall(owner)
            self.assertTrue(ids, f"a finding has no bug, CR or decision id: {row}")
            for rec in ids:
                found = rec in decided if rec.startswith("D") else sdlc_md.find_by_id(REPO, rec)
                self.assertTrue(found, f"{rec} does not resolve in this workspace")


if __name__ == "__main__":
    unittest.main()
