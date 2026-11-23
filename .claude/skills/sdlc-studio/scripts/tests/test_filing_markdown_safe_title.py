"""BG0974: the filer markdown-safes a finding's title and its Evidence line, so a bare
`snake_case` or leading-underscore identifier there is written inside a code span and
markdownlint's MD037 passes on the bug file and on the index row.

Each finding is filed through the shipped CLI (`file_finding.py file`) into a throwaway fixture
root (`--root`).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_filing_markdown_safe_title.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/file_finding.py
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import file_finding  # noqa: E402
import gitutil  # noqa: E402 - confined git, so an inherited GIT_DIR cannot steer the lookup

SCRIPT = Path(__file__).resolve().parent.parent / "file_finding.py"
SKILL = SCRIPT.parent.parent
CONFIG = SKILL / ".markdownlint.json"

EVIDENCE = ("BG0959 Evidence line: _mode_and_cutoff in test_lean_backlog_sweep, "
            "see file_finding.py:2011")


def _markdownlint() -> str | None:
    """The markdownlint the repo's lane runs: on PATH, in this checkout, or in the main checkout
    this worktree hangs off (a worktree carries no `node_modules` of its own)."""
    found = shutil.which("markdownlint")
    if found:
        return found
    roots = [SKILL.parents[1]]
    common = gitutil.git(["rev-parse", "--path-format=absolute", "--git-common-dir"], SKILL,
                         check=False, text=True)
    if common.returncode == 0 and common.stdout.strip():
        roots.append(Path(common.stdout.strip()).parent)
    for root in roots:
        cand = root / "node_modules" / ".bin" / "markdownlint"
        if cand.exists():
            return str(cand)
    return None


def _bare(line: str) -> str:
    """The line with every code span removed: what markdown reads as text."""
    return re.sub(r"`[^`]*`", "", line)


def _file(root: Path, title: str, type_: str = "bug", *extra: str) -> tuple[str, str]:
    """File one finding; return its H1 line and its index row."""
    (root / "src").mkdir(exist_ok=True)
    (root / "src" / "thing.py").write_text("", encoding="utf-8")
    file_finding.ensure_index(root, type_, "2026-11-23")  # the shipped index template
    typed = (["--severity", "low", "--points", "1", "--summary", "s", "--steps", "r",
              "--fix", "f", "--ac", "it holds", "--verify", "pytest tests/test_x.py"]
             if type_ == "bug" else ["--summary", "s"])
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "file", "--root", str(root), "--type", type_,
         "--title", title, "--affects", "src/thing.py", "--author", "Tess Tester",
         *typed, *extra], capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise AssertionError(f"the filer refused the fixture finding:\n{r.stdout}{r.stderr}")
    folder = {"bug": "bugs", "rfc": "rfcs"}[type_]
    path = next(p for p in (root / "sdlc-studio" / folder).glob("*.md") if p.name != "_index.md")
    index = (root / "sdlc-studio" / folder / "_index.md").read_text(encoding="utf-8")
    row = next(ln for ln in index.splitlines() if ln.startswith("| [") and path.name in ln)
    return path.read_text(encoding="utf-8"), row


class TitleIdentifierTests(unittest.TestCase):
    """AC1: the H1 and the index row of a title holding bare identifiers."""

    TITLE = "test_lean_backlog_sweep reads only the live _index.md"
    SAFE = "`test_lean_backlog_sweep` reads only the live `_index.md`"

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.body, self.row = _file(Path(self._td.name), self.TITLE)
        self.h1 = self.body.splitlines()[0]

    def tearDown(self) -> None:
        self._td.cleanup()

    def test_title_identifier_is_code_spanned_in_the_h1(self) -> None:
        self.assertEqual(self.h1, f"# BG0001: {self.SAFE}")
        self.assertNotIn("_", _bare(self.h1))

    def test_title_identifier_is_code_spanned_in_the_index_row(self) -> None:
        self.assertIn(f"| {self.SAFE} |", self.row)
        self.assertNotIn("_", _bare(self.row))

    def test_title_identifier_is_code_spanned_in_an_rfcs_h1_and_row(self) -> None:
        """The title is safed for every type the filer mints, not the bug layout alone."""
        with tempfile.TemporaryDirectory() as d:
            body, row = _file(Path(d), "keep _cache_dir apart", "rfc", "--option", "do it")
        self.assertTrue(body.splitlines()[0].endswith(": keep `_cache_dir` apart"), body)
        self.assertIn("| keep `_cache_dir` apart |", row)

    def test_the_file_name_is_still_slugged_from_the_title_words(self) -> None:
        self.assertIn("(BG0001-test-lean-backlog-sweep-reads-only-the-live.md)", self.row)


class EvidenceIdentifierTests(unittest.TestCase):
    """AC2: the Evidence line."""

    def test_evidence_identifier_is_code_spanned(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            body, _row = _file(Path(d), "a plain title", "bug", "--evidence", EVIDENCE)
        line = next(ln for ln in body.splitlines() if ln.startswith("> **Evidence:** "))
        value = line[len("> **Evidence:** "):]
        self.assertEqual(value, "BG0959 Evidence line: `_mode_and_cutoff` in "
                                "`test_lean_backlog_sweep`, see `file_finding.py`:2011")
        self.assertNotIn("_", _bare(value))
        self.assertEqual(value.replace("`", ""), EVIDENCE)  # otherwise byte-identical


class TitleMarkdownTests(unittest.TestCase):
    """AC3: a title holding two identifiers that begin with underscores, filed, passes
    markdownlint in the bug file and in the index."""

    TITLE = "_mode_and_cutoff and _check disagree"

    @classmethod
    def setUpClass(cls) -> None:
        cls._td = tempfile.TemporaryDirectory()
        cls.root = Path(cls._td.name)
        cls.body, cls.row = _file(cls.root, cls.TITLE)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._td.cleanup()

    def _lint(self, path: Path) -> subprocess.CompletedProcess:
        lint = _markdownlint()
        if lint is None:
            self.skipTest("markdownlint is not installed (npm install) - the lint lane enforces this")
        return subprocess.run([lint, "-c", str(CONFIG), str(path)], capture_output=True,
                              text=True, check=False)

    def test_neither_line_holds_an_underscore_outside_a_code_span(self) -> None:
        """Runs with or without markdownlint: the underscores MD037 reads as emphasis."""
        self.assertNotIn("_", _bare(self.body.splitlines()[0]))
        self.assertNotIn("_", _bare(self.row))

    def test_the_bug_file_passes_markdownlint(self) -> None:
        path = next((self.root / "sdlc-studio" / "bugs").glob("BG*.md"))
        r = self._lint(path)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_the_index_passes_markdownlint(self) -> None:
        r = self._lint(self.root / "sdlc-studio" / "bugs" / "_index.md")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
