"""BG1427: `file_finding.py file --parent` wrote the parent's `Decomposed-into` line but not the
spawned-work cell of its index row, so `reconcile.py detect` then reported a spawned-column drift
item and the next commit was refused. The filer now brings that cell up to date in the same lock
as the mint.

Each case files through the shipped CLI (`file_finding.py file`) into a throwaway fixture root
(`--root`) and reads the drift with `reconcile.spawned_column_drift`.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_file_finding_parent_index_cell.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/file_finding.py
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import file_finding  # noqa: E402
import reconcile  # noqa: E402

SCRIPT = Path(__file__).resolve().parent.parent / "file_finding.py"


def _file(root: Path, type_: str, title: str, *extra: str) -> subprocess.CompletedProcess:
    """One finding filed through the CLI; the completed process."""
    (root / "src").mkdir(exist_ok=True)
    (root / "src" / "thing.py").write_text("", encoding="utf-8")
    typed = {"rfc": ["--option", "do it"], "cr": ["--priority", "Low"]}[type_]
    return subprocess.run(
        [sys.executable, str(SCRIPT), "file", "--root", str(root), "--type", type_,
         "--title", title, "--affects", "src/thing.py", "--author", "Tess Tester",
         "--summary", "s", *typed, *extra], capture_output=True, text=True, check=False)


def _cell(root: Path, rfc_id: str) -> str:
    """The `Decomposed into` cell of one RFC's index row."""
    index = (root / "sdlc-studio" / "rfcs" / "_index.md").read_text(encoding="utf-8")
    row = next(ln for ln in index.splitlines() if ln.startswith("| [") and rfc_id in ln)
    return row.strip().strip("|").split(" | ")[-1].strip()


class ParentIndexCellTests(unittest.TestCase):

    def setUp(self) -> None:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.root = Path(td.name)
        file_finding.ensure_index(self.root, "rfc", "2026-11-24")
        file_finding.ensure_index(self.root, "cr", "2026-11-24")
        r = _file(self.root, "rfc", "the parent request")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)

    def _drift(self) -> list[dict]:
        return reconcile.spawned_column_drift(self.root)

    def test_a_child_filed_under_a_parent_leaves_no_spawned_column_drift(self) -> None:
        """AC1. Mutant: the parent's `Decomposed-into` written and its index cell left alone."""
        self.assertEqual([], self._drift(), "premise: a fresh parent row agrees with the census")
        r = _file(self.root, "cr", "the first child", "--parent", "RFC-0001")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual([], self._drift())
        self.assertIn("CR0001", _cell(self.root, "RFC-0001"))

    def test_a_second_child_is_added_beside_the_first(self) -> None:
        """Mutant: the cell rewritten from the new child alone."""
        for title in ("the first child", "the second child"):
            r = _file(self.root, "cr", title, "--parent", "RFC-0001")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        cell = _cell(self.root, "RFC-0001")
        self.assertIn("CR0001", cell)
        self.assertIn("CR0002", cell)
        self.assertEqual([], self._drift())

    def test_a_finding_without_a_parent_leaves_the_cell_alone(self) -> None:
        """The control: a child nobody names a parent for is nobody's spawned work."""
        before = _cell(self.root, "RFC-0001")
        r = _file(self.root, "cr", "an orphan")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual(before, _cell(self.root, "RFC-0001"))
        self.assertEqual([], self._drift())

    def test_a_refused_parent_mints_nothing_and_moves_no_cell(self) -> None:
        """The control beside the refusal: a parent that does not resolve is refused before any
        id is minted, and the existing parent's cell is as it was."""
        before = _cell(self.root, "RFC-0001")
        r = _file(self.root, "cr", "a lost child", "--parent", "RFC-0099")
        self.assertNotEqual(0, r.returncode)
        self.assertIn("does not resolve", r.stdout + r.stderr)
        self.assertEqual(before, _cell(self.root, "RFC-0001"))
        self.assertFalse(list((self.root / "sdlc-studio" / "change-requests").glob("CR*.md")))

    def test_a_cell_of_another_index_is_not_touched(self) -> None:
        """The sync is the parent's own index: a drifted RFC row stays as it was when the
        parent is a CR. Mutant: every request index synced."""
        r = _file(self.root, "cr", "a middle request", "--parent", "RFC-0001")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        index = self.root / "sdlc-studio" / "rfcs" / "_index.md"
        index.write_text(index.read_text(encoding="utf-8").replace("CR0001", "--"),
                         encoding="utf-8")
        self.assertEqual(["RFC0001"], [d["id"] for d in self._drift()], "premise: one RFC drift")
        r = _file(self.root, "cr", "a grandchild", "--parent", "CR-0001")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual("--", _cell(self.root, "RFC-0001"))
        self.assertEqual(["RFC0001"], [d["id"] for d in self._drift()])

    def test_a_dry_run_writes_no_cell(self) -> None:
        """Mutant: the cell synced in a preview, which writes nothing else."""
        r = _file(self.root, "cr", "a first child", "--parent", "RFC-0001")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        index = self.root / "sdlc-studio" / "rfcs" / "_index.md"
        index.write_text(index.read_text(encoding="utf-8").replace("CR0001", "--"),
                         encoding="utf-8")
        before = _cell(self.root, "RFC-0001")
        self.assertEqual("--", before, "premise: the cell disagrees with the census")
        r = _file(self.root, "cr", "a previewed child", "--parent", "RFC-0001", "--dry-run")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual(before, _cell(self.root, "RFC-0001"))


if __name__ == "__main__":
    unittest.main()
