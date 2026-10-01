"""BG0868: `refine add --into <epic>` adds a story to a request's existing epic.

`refine add` could only mint a further epic, so a story for an epic the request was already
decomposed into was minted by hand with `artifact.py new` and a hand-written `Delivers:`. Each
test drives the shipped `refine.py` as a subprocess against a throwaway tree: `apply` makes the
first epic, then `add --into` adds to it.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent

_CR = ("# CR-0001: a request\n\n> **Status:** Approved\n> **Priority:** P1\n"
       "> **Type:** Improvement\n> **Size:** L\n> **Affects:** src/a.py\n\n## Summary\n\ns\n\n"
       "## Acceptance Criteria\n\n- [ ] the request is satisfied\n\n## Impact\n\ni\n")


def _refine(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "refine.py"), *args, "--root", str(root)],
        capture_output=True, text=True, check=False, timeout=120)


class RefineAddIntoTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "a.py").write_text("", encoding="utf-8")
        crs = self.root / "sdlc-studio" / "change-requests"
        crs.mkdir(parents=True)
        self.cr = crs / "CR0001-a-request.md"
        self.cr.write_text(_CR, encoding="utf-8")
        first = _refine(self.root, "apply", "--request", "CR0001", "--epic-title", "First slice",
                        "--story", "A|2|src/a.py", "--skip-personas")
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        self.epics = sorted((self.root / "sdlc-studio" / "epics").glob("EP*.md"))
        self.assertEqual(1, len(self.epics))
        self.epic = self.epics[0].name.split("-", 1)[0]

    def _stories(self) -> dict[str, str]:
        return {p.name: p.read_text(encoding="utf-8")
                for p in (self.root / "sdlc-studio" / "stories").glob("US*.md")}

    def test_add_into_the_existing_epic(self) -> None:
        """AC1. MUTANT: HEAD, which refuses `--into` on `add`. MUTANT: the CLI parses `--into`
        and drops it - `add` then asks for an epic title. MUTANT: mint a bare story under the
        epic, as `artifact.py new --epic` does - it carries no `Delivers:` line."""
        before = set(self._stories())
        proc = _refine(self.root, "add", "--request", "CR0001", "--into", self.epic,
                       "--story", "B|1|src/a.py")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertEqual(self.epics, sorted((self.root / "sdlc-studio" / "epics").glob("EP*.md")),
                         "a new epic was minted")
        new = {k: v for k, v in self._stories().items() if k not in before}
        self.assertEqual(1, len(new), new.keys())
        body = next(iter(new.values()))
        self.assertRegex(body, rf"> \*\*Epic:\*\* {self.epic}\b")
        self.assertIn("> **Delivers:** CR0001", body)
        decomposed = re.search(r"> \*\*Decomposed-into:\*\* (.*)", self.cr.read_text("utf-8"))
        self.assertEqual(self.epic, decomposed.group(1).strip())

    def test_add_takes_one_target_not_both(self) -> None:
        """`--into` and `--epic-title` name two different targets. MUTANT: let `--epic-title`
        win silently - a new epic is minted and `--into` ignored."""
        proc = _refine(self.root, "add", "--request", "CR0001", "--into", self.epic,
                       "--epic-title", "Second", "--story", "B|1|src/a.py")
        self.assertEqual(2, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("not both", proc.stderr)
        self.assertEqual(self.epics, sorted((self.root / "sdlc-studio" / "epics").glob("EP*.md")))


if __name__ == "__main__":
    unittest.main()
