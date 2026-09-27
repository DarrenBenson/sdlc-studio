"""BG0805: `verify_ac.py stamps` resolves each `or`-joined `-k` term on its own.

A stamped `pytest <file> -k "a or b"` was resolved as one expression, so a live `a` hid a dead
`b`: the stamp read green while the half of the claim `b` stood for verified nothing. Eight such
terms sat in this repository behind a `stamps --bugs` that exited 0.
"""
from __future__ import annotations

import contextlib
import io
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
SCRIPT = SCRIPTS / "verify_ac.py"
REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(SCRIPTS))

import verify_ac  # noqa: E402

TEST_X = "def test_alpha():\n    pass\n\n\ndef test_gamma():\n    pass\n"
TEST_Y = "def test_delta():\n    pass\n"


def _unit(path: Path, uid: str, verifier: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# {uid}: a stamped criterion\n\n> **Status:** Done\n\n"
        "## Acceptance Criteria\n\n### AC1: it holds\n\n"
        f"- **Verify:** {verifier}\n- **Verified:** yes (2026-09-27)\n", encoding="utf-8")


#: The terms the bug was filed for, by the artefact whose stamp carried each.
DEAD_AT_FILING = {
    "US0062": ("cr_without_effort_fails", "cr_with_impact_and_effort_passes"),
    "US0077": ("root_is_alias_of_repo_root",),
    "US0081": ("batch_defaults_to_full_template",),
    # BG0264's third, `test_a_mixed_target_list_is_not_refused`, is not here: the test was
    # deleted with no replacement and is restored under its own name, so the term is live and
    # the stamps run above judges it.
    "BG0264": ("test_file_verb_on_markdown_is_refused", "test_uppercase_extension_is_refused"),
    "BG0555": ("root_is_a_global_flag",),
}


class StampsKTermTests(unittest.TestCase):

    def _stamps(self, root: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "stamps", "--bugs", "--root", str(root)],
            capture_output=True, text=True, timeout=300, cwd=str(root))

    def test_a_dead_k_term_is_named(self) -> None:
        """AC1. MUTANT: HEAD - the expression resolved as a whole, so `alpha` hides `beta` and
        stamps exits 0. Controls: two live terms exit 0; a term live only in the selector's
        SECOND file is not dead (pytest's -k spans every file named); an expression whose every
        term is dead is reported once, as selecting nothing, not twice."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "tests").mkdir()
            (root / "tests" / "test_x.py").write_text(TEST_X, encoding="utf-8")
            (root / "tests" / "test_y.py").write_text(TEST_Y, encoding="utf-8")
            stories = root / "sdlc-studio" / "stories"
            bugs = root / "sdlc-studio" / "bugs"

            _unit(stories / "US0001-x.md", "US0001", 'pytest tests/test_x.py -k "alpha or beta"')
            proc = self._stamps(root)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            named = [ln for ln in proc.stdout.splitlines() if ln.startswith("US0001 AC1")]
            self.assertEqual(len(named), 1, proc.stdout)
            self.assertIn("'beta'", named[0], "the dead term must be named")
            self.assertNotIn("'alpha'", named[0], "a live term is not dead")

            # A parenthesised group is one term: split inside it and the dead group hides.
            _unit(stories / "US0001-x.md", "US0001",
                  'pytest tests/test_x.py -k "(beta or zeta) or alpha"')
            proc = self._stamps(root)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("beta or zeta", proc.stdout)

            _unit(stories / "US0001-x.md", "US0001", 'pytest tests/test_x.py -k "alpha or gamma"')
            _unit(bugs / "BG0001-x.md", "BG0001",
                  'pytest tests/test_x.py tests/test_y.py -k "alpha or delta"')
            proc = self._stamps(root)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            _unit(bugs / "BG0001-x.md", "BG0001", 'pytest tests/test_x.py -k "zeta or delta"')
            proc = self._stamps(root)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertEqual(proc.stdout.count("BG0001 AC1"), 1, proc.stdout)
            self.assertIn("selects nothing", proc.stdout)

    def test_the_repository_carries_no_dead_k_term(self) -> None:
        """AC2, on this repository. MUTANT: restore any one of the eight terms to its stamp.

        `stamps` runs through `main` over every stamped unit whose `-k` carries a top-level
        `or`, sharing one collection cache, rather than as `stamps --bugs` over the whole
        corpus: that run collects every stamped test file, about a minute, and this module
        is selected on any commit touching `verify_ac.py` (the budget BG0807 repaired). The
        units it skips carry no `or`-joined term, so the whole-corpus run adds nothing here
        that `unresolvable_stamps` does not already judge."""
        units = []
        for sub in ("sdlc-studio/stories", "sdlc-studio/bugs"):
            for path in sorted((REPO / sub).glob("*.md")):
                text = path.read_text(encoding="utf-8", errors="replace")
                for block in verify_ac.criteria_blocks(text):
                    if ((block.verified_state or "").strip().lower() == "yes" and block.verifier
                            and re.search(r"-k\s+[\"'][^\"']*\bor\b", block.verifier)):
                        units.append(path)
                        break
        self.assertTrue(units, "no stamped or-joined -k selector found: the scan reads nothing")
        for path in units:
            with self.subTest(unit=path.name):
                out = io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                    rc = verify_ac.main(["stamps", "--story", str(path), "--root", str(REPO)])
                self.assertEqual(rc, 0, out.getvalue())
        for uid, terms in DEAD_AT_FILING.items():
            (path,) = [p for sub in ("stories", "bugs")
                       for p in (REPO / "sdlc-studio" / sub).glob(f"{uid}-*.md")]
            verifiers = " ".join(b.verifier or "" for b in verify_ac.criteria_blocks(
                path.read_text(encoding="utf-8")))
            for term in terms:
                with self.subTest(unit=uid, term=term):
                    self.assertNotRegex(verifiers, rf"\b{term}\b")


if __name__ == "__main__":
    unittest.main()
