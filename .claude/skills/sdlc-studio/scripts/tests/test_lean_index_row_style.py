"""BG0867: a status transition keeps a padded index table lint-clean.

`transition.py set` synced the index row compact (`| a | b |`) beneath a header and separator
padded to aligned column widths, so markdownlint failed MD060 (table-column-style) on the index
and the next commit was refused. The table a row is written into now keeps its own style. Each
test drives the shipped `transition.py set` against a throwaway workspace; the structural check
(every row's pipes in the header's columns) runs everywhere, and markdownlint itself runs where
it is installed.
"""
from __future__ import annotations

# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import sdlc_md  # noqa: E402
REPO = SCRIPTS.parents[3]
MDL = REPO / "node_modules" / ".bin" / "markdownlint"

_INDEX = """# Test Spec Registry

## Summary

| Status | Count |
| --- | --- |
| Draft | 2 |
| Complete | 0 |
| **Total** | **2** |

## All

| ID                       | Title       | Epic   | Status |
| ------------------------ | ----------- | ------ | ------ |
| [TS0001](TS0001-spec.md) | first spec  | EP0010 | Draft  |
| [TS0002](TS0002-spec.md) | second spec | EP0010 | Draft  |
"""


def _pipes(line: str) -> list[int]:
    return [m.start() for m in re.finditer(r"(?<!\\)\|", line)]


class IndexRowStyleTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        specs = self.root / "sdlc-studio" / "test-specs"
        specs.mkdir(parents=True)
        for n, title in ((1, "first spec"), (2, "second spec")):
            (specs / f"TS000{n}-spec.md").write_text(
                f"# TS000{n}: {title}\n\n> **Status:** Draft\n> **Epic:** EP0010\n",
                encoding="utf-8")
        self.index = specs / "_index.md"
        self.index.write_text(_INDEX, encoding="utf-8")

    def _set(self, sid: str, status: str) -> None:
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "transition.py"), "set", "--id", sid,
             "--status", status, "--root", str(self.root)],
            capture_output=True, text=True, check=False, timeout=120)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)

    def test_a_synced_row_matches_a_padded_table(self) -> None:
        """AC1. MUTANT: HEAD, which writes the synced row compact under the padded header.
        MUTANT: pad the synced row to the OLD widths - `Complete` is wider than the `Status`
        column was, so its pipe lands out of line unless the whole table is re-measured."""
        self._set("TS0001", "Complete")
        lines = self.index.read_text(encoding="utf-8").splitlines()
        start = lines.index(next(ln for ln in lines if ln.startswith("| ID")))
        table = lines[start:start + 4]
        self.assertIn("Complete", table[2])
        for ln in table[1:]:
            self.assertEqual(_pipes(table[0]), _pipes(ln), "\n".join(table))
        # the compact Summary table above is left compact
        self.assertIn("| Draft | 1 |", lines)
        if not MDL.is_file():                       # pragma: no cover - npm install not run
            self.skipTest(f"{MDL} not installed; the structural check above still ran")
        proc = subprocess.run([str(MDL), str(self.index)], capture_output=True, text=True)
        self.assertNotIn("MD060", proc.stdout + proc.stderr, proc.stdout + proc.stderr)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)

    def test_alignment_keeps_markers_escapes_and_examples(self) -> None:
        """The re-alignment keeps what the table says. MUTANTS: drop the separator's `:`
        alignment markers; measure a cell after unescaping `\\|` (its pipe then splits the
        row); reflow a table inside a fenced example."""
        text = ("| Name | Value       |\n| :--- | ----------: |\n| a | x \\| y |\n\n"
                "```markdown\n| Name | Value       |\n| ---- | ----------- |\n| b | 1 |\n```\n")
        out = sdlc_md.align_padded_tables(text)
        lines = out.splitlines()
        self.assertEqual("| :--- | ----------: |", lines[1])
        self.assertEqual("| a    | x \\| y      |", lines[2])
        self.assertEqual(_pipes(lines[0]), _pipes(lines[2]))
        self.assertIn("| b | 1 |", lines, "a fenced example was reflowed")
        self.assertEqual(out, sdlc_md.align_padded_tables(out), "not idempotent")
        # a compact table whose header happens to match its separator is still compact
        compact = "| Abc | Def |\n| --- | --- |\n| a longer value | x |\n"
        self.assertEqual(compact, sdlc_md.align_padded_tables(compact))

    def _lint(self) -> None:
        if not MDL.is_file():                       # pragma: no cover - npm install not run
            return
        proc = subprocess.run([str(MDL), str(self.index)], capture_output=True, text=True)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)

    def test_an_untouched_wide_character_table_is_left_byte_for_byte(self) -> None:
        """Round-1 repro. A compact data table, a padded Glossary holding CJK (lint-clean,
        aligned by display width) and a padded Totals table with a right-aligned count, neither
        touched by the write. MUTANT: reflow every aligned table in the index - Totals is
        re-rendered."""
        glossary = ("## Glossary\n\n| Term   | Meaning    |\n| ------ | ---------- |\n"
                    "| 用語   | a term     |\n| plain  | not a term |\n\n"
                    "## Totals\n\n| Kind      | Count |\n| --------- | ----: |\n"
                    "| specs     |     2 |\n")
        self.index.write_text(_INDEX.replace(
            "| ID                       | Title       | Epic   | Status |\n"
            "| ------------------------ | ----------- | ------ | ------ |\n"
            "| [TS0001](TS0001-spec.md) | first spec  | EP0010 | Draft  |\n"
            "| [TS0002](TS0002-spec.md) | second spec | EP0010 | Draft  |\n",
            "| ID | Title | Epic | Status |\n| --- | --- | --- | --- |\n"
            "| [TS0001](TS0001-spec.md) | first spec | EP0010 | Draft |\n"
            "| [TS0002](TS0002-spec.md) | second spec | EP0010 | Draft |\n") + "\n" + glossary,
            encoding="utf-8")
        self._lint()
        self._set("TS0001", "Complete")
        text = self.index.read_text(encoding="utf-8")
        self.assertIn("| [TS0001](TS0001-spec.md) | first spec | EP0010 | Complete |", text)
        self.assertTrue(text.endswith(glossary), text)
        self._lint()

    def test_a_table_holding_an_unmeasured_character_is_left_alone(self) -> None:
        """A wide or combining character is measured by display width (BG0889); an emoji joined
        by a zero-width joiner takes the width of its grapheme cluster, which a per-character
        sum gets wrong, so its table is not reflowed even when a row in it was rewritten.
        MUTANT: drop the unmeasured-character skip - the table is re-padded by a width MD060
        does not use."""
        coder = "dev \U0001F469\u200D\U0001F4BB"         # woman + ZWJ + laptop: one cluster
        spec = self.index.parent / "TS0002-spec.md"
        spec.write_text(spec.read_text(encoding="utf-8").replace("second spec", coder),
                        encoding="utf-8")
        self.index.write_text(_INDEX.replace("| second spec |", f"| {coder}   |"),
                              encoding="utf-8")
        before = self.index.read_text(encoding="utf-8").splitlines()
        self._set("TS0001", "Complete")
        after = self.index.read_text(encoding="utf-8").splitlines()
        changed = [(a, b) for a, b in zip(before, after) if a != b]
        self.assertEqual(["| [TS0001](TS0001-spec.md) | first spec | EP0010 | Complete |"],
                         [b for a, b in changed if a.startswith("| [TS0001]")], changed)
        self.assertEqual([], [b for a, b in changed if a.startswith(("| ID", "| ---", "| [TS0002]"))])

    def test_a_ragged_table_is_left_alone(self) -> None:
        """A row with more cells than the separator is not a table this can reflow. MUTANT:
        drop the ragged check - the extra cell is lost or the row re-padded wrongly."""
        text = ("| Name   | Value |\n| ------ | ----- |\n| a | b | extra |\n")
        self.assertEqual(text, sdlc_md.align_padded_tables(text))


if __name__ == "__main__":
    unittest.main()
