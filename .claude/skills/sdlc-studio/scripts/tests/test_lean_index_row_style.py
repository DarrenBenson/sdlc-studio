"""BG0867: a status transition keeps a padded index table lint-clean.

`transition.py set` synced the index row compact (`| a | b |`) beneath a header and separator
padded to aligned column widths, so markdownlint failed MD060 (table-column-style) on the index
and the next commit was refused. The table a row is written into now keeps its own style. Each
test drives the shipped `transition.py set` against a throwaway workspace; the structural check
(every row's pipes in the header's columns) runs everywhere, and markdownlint itself runs where
it is installed.
"""
from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
