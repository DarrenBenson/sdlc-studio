"""The Status Vocabulary table in reference-outputs.md says what the code enforces.

Every gate reads `sdlc_md.STATUS_VOCAB` and `sdlc_md.TERMINAL_STATUS`; an agent following the
reference reads the table. The two disagreed on bug, story, CR and RFC terminals and lacked the
issue and charter rows, so this compares them row by row, both columns, both directions.
"""
# test-census-subject: .claude/skills/sdlc-studio/reference-outputs.md
from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import sdlc_md  # noqa: E402

PAGE = SCRIPTS.parent / "reference-outputs.md"
HEADING = "## Status Vocabulary Enforcement"
HEADER = "| Type | Allowed Statuses | Terminal |"

#: The table's display names whose code key is not simply the name lowercased.
DISPLAY_KEY = {"Test Spec": "test-spec"}


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _statuses(cell: str) -> set[str]:
    return {s.strip() for s in cell.split(",") if s.strip()}


def table_lines(text: str) -> list[str]:
    """The body rows of the section's first table: after its header and delimiter, up to the
    first line that is not a row. A later table in a subsection is not this one."""
    lines = text.split(HEADING, 1)[1].splitlines()
    start = lines.index(HEADER) + 2          # the header, then its delimiter row
    out = []
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        out.append(line)
    return out


def table_rows(text: str) -> list[tuple[str, set[str], set[str]]]:
    """`[(type key, allowed, terminal)]`, one per row of the table, in page order."""
    rows = []
    for line in table_lines(text):
        name, allowed, terminal = _cells(line)
        rows.append((DISPLAY_KEY.get(name, name.lower()), _statuses(allowed), _statuses(terminal)))
    return rows


def divergences(rows, vocab, terminal) -> list[str]:
    """Every way the table and the code disagree, each naming its type and its status."""
    out: list[str] = []
    seen: dict[str, int] = {}
    for key, _, _ in rows:
        seen[key] = seen.get(key, 0) + 1
    for key in sorted(set(vocab) | set(seen)):
        if key not in seen:
            out.append(f"{key}: no row in the table")
        elif key not in vocab:
            out.append(f"{key}: a row for a type the code does not know")
        elif seen[key] > 1:
            out.append(f"{key}: {seen[key]} rows, not one")
    for key, allowed, term in rows:
        if key not in vocab:
            continue
        code_allowed, code_term = set(vocab[key]), set(terminal.get(key, ()))
        out += [f"{key}: allowed lacks {s}" for s in sorted(code_allowed - allowed)]
        out += [f"{key}: allowed lists {s}, which the code does not" for s in sorted(allowed - code_allowed)]
        out += [f"{key}: terminal lacks {s}" for s in sorted(code_term - term)]
        out += [f"{key}: terminal lists {s}, which the code does not" for s in sorted(term - code_term)]
    return out


class StatusVocabDocTests(unittest.TestCase):

    def test_the_table_matches_the_code(self) -> None:
        """AC1: one row per type in STATUS_VOCAB, issue and charter included, each row's
        allowed and terminal sets equal to the code's."""
        rows = table_rows(PAGE.read_text(encoding="utf-8"))
        self.assertEqual(sorted(k for k, _, _ in rows), sorted(sdlc_md.STATUS_VOCAB))
        self.assertEqual(divergences(rows, sdlc_md.STATUS_VOCAB, sdlc_md.TERMINAL_STATUS), [])

    def test_a_divergence_names_the_type_and_status(self) -> None:
        """AC2: a copy of the corrected table with one terminal status removed from one row fails
        the comparison, naming that type and that status. Tried for every terminal status of
        every row, so a comparison of row counts, or of the allowed column only, cannot pass."""
        text = PAGE.read_text(encoding="utf-8")
        tried = 0
        for line in table_lines(text):
            name, _, terminal_cell = _cells(line)
            key = DISPLAY_KEY.get(name, name.lower())
            for status in sorted(_statuses(terminal_cell)):
                with self.subTest(type=key, status=status):
                    kept = ", ".join(s for s in sorted(_statuses(terminal_cell)) if s != status)
                    copy = text.replace(line, line.rsplit("|", 2)[0] + f"| {kept} |", 1)
                    self.assertNotEqual(copy, text, "the copy really lost the status")
                    found = divergences(table_rows(copy), sdlc_md.STATUS_VOCAB,
                                        sdlc_md.TERMINAL_STATUS)
                    self.assertEqual(found, [f"{key}: terminal lacks {status}"])
                    tried += 1
        self.assertGreaterEqual(tried, len(sdlc_md.STATUS_VOCAB), "every row has a terminal")

    def test_every_kind_of_divergence_is_named(self) -> None:
        """The comparator's other branches, each fed a copy of the table that trips only it: a
        correct page passes with any of them deleted, so only a divergent copy pins them."""
        text = PAGE.read_text(encoding="utf-8")
        rows = {ln.split("|")[1].strip(): ln for ln in table_lines(text)}
        cases = {
            "bug: terminal lists Open, which the code does not":
                text.replace(rows["Bug"], rows["Bug"].rstrip(" |") + ", Open |"),
            "story: allowed lacks Blocked": text.replace(rows["Story"],
                                                         rows["Story"].replace("Blocked, ", "")),
            "plan: allowed lists Active, which the code does not":
                text.replace(rows["Plan"], rows["Plan"].replace("| Draft,", "| Active, Draft,")),
            "charter: no row in the table": text.replace(rows["Charter"] + "\n", ""),
            "epic: 2 rows, not one": text.replace(rows["Epic"], rows["Epic"] + "\n" + rows["Epic"]),
            "widget: a row for a type the code does not know":
                text.replace(rows["Epic"], rows["Epic"] + "\n| Widget | Open | Open |"),
        }
        for expected, copy in cases.items():
            with self.subTest(expected=expected):
                self.assertNotEqual(copy, text)
                self.assertEqual(divergences(table_rows(copy), sdlc_md.STATUS_VOCAB,
                                             sdlc_md.TERMINAL_STATUS), [expected])

if __name__ == "__main__":
    unittest.main()
