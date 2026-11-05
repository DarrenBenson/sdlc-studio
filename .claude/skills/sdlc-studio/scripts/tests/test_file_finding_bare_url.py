"""BG1227: the filer code-spans a bare http(s) URL in a finding's prose, so markdownlint's MD034
(no bare URLs) passes on the file it writes, and leaves a URL already spanned or linked alone.

Each finding is filed through the shipped CLI into a throwaway fixture repo (`--root`).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_file_finding_bare_url.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/file_finding.py
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402 - confined git, so an inherited GIT_DIR cannot steer the lookup

SCRIPT = Path(__file__).resolve().parent.parent / "file_finding.py"
SKILL = SCRIPT.parent.parent
CONFIG = SKILL / ".markdownlint.json"

SUMMARY = ("The page at http://127.0.0.1:8080/x_y answers 500, see `https://ok.example/a` and "
           "<https://auto.example/b>, or [the doc](https://link.example/c).")
STEPS = "1. Open http://127.0.0.1:8080.\n2. Read xhttps://not.example and _https://mirror.example/g."
FIX = "Serve (https://paren.example/d)."
AC = "the page at https://ac.example/e answers 200"
EVIDENCE = "the log at https://ev.example/f"


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


class FiledBareUrlTests(unittest.TestCase):
    """One bug filed through `file_finding.py file`, carrying a URL in every prose field."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._td = tempfile.TemporaryDirectory()
        root = Path(cls._td.name)
        (root / "src").mkdir()
        (root / "src" / "thing.py").write_text("", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "file", "--root", str(root), "--type", "bug",
             "--title", "a server answers", "--severity", "low", "--points", "1",
             "--affects", "src/thing.py", "--summary", SUMMARY, "--steps", STEPS, "--fix", FIX,
             "--ac", AC, "--verify", "pytest tests/test_x.py", "--evidence", EVIDENCE],
            capture_output=True, text=True, check=False)
        if r.returncode != 0:
            cls._td.cleanup()
            raise AssertionError(f"the filer refused the fixture finding:\n{r.stdout}{r.stderr}")
        cls.path = next((root / "sdlc-studio" / "bugs").glob("BG*.md"))
        cls.body = cls.path.read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._td.cleanup()

    def test_the_filed_file_passes_the_markdown_lane(self) -> None:
        """AC1, through the tool that refused BG1225's commit, under the skill's own config.
        MUTANTS: (1) `_md_safe` without the `_code_urls` pass - MD034 on the summary, steps,
        fix and criterion lines; (2) `_evidence_line` without it - MD034 on the Evidence line."""
        mdl = _markdownlint()
        if mdl is None:
            self.skipTest("markdownlint is not installed (npm install) - the lint lane enforces this")
        r = subprocess.run([mdl, "--config", str(CONFIG), "--", str(self.path)],
                           capture_output=True, text=True, check=False)
        out = r.stdout + r.stderr
        self.assertNotIn("MD034", out, f"the filer wrote a bare URL:\n{out}\n{self.body}")
        self.assertEqual(0, r.returncode, f"the filed file fails the markdown lane:\n{out}")

    def test_each_bare_url_becomes_one_whole_code_span(self) -> None:
        """MUTANTS: (1) the underscore-token pass run before the URL pass - `x_y` is spanned
        inside the address and the URL is split in two; (2) no trailing-punctuation trim - the
        full stop goes inside the span; (3) no unbalanced-`)` trim - the bracket goes inside;
        (4) `\\w` in the lookbehind - the URL after `_` stays bare, though markdownlint reports
        MD034 on `see_https://...`; (5) no letter-or-digit lookbehind - the URL glued to a
        letter, where markdownlint reports none, is spanned."""
        for want in ("The page at `http://127.0.0.1:8080/x_y` answers 500,",
                     "1. Open `http://127.0.0.1:8080`.",
                     "2. Read xhttps://not.example and _`https://mirror.example/g`.",
                     "Serve (`https://paren.example/d`).",
                     "the page at `https://ac.example/e` answers 200",
                     "> **Evidence:** the log at `https://ev.example/f`\n"):
            self.assertIn(want, self.body)

    def test_a_url_already_spanned_or_linked_is_left_as_it_is(self) -> None:
        """MUTANTS: (1) the URL pass run over the whole text, not only outside code spans - the
        spanned URL is double-wrapped; (2) no `<` lookbehind - the autolink gains backticks;
        (3) no `](` lookbehind - the link destination gains backticks and the link breaks."""
        self.assertIn("see `https://ok.example/a` and <https://auto.example/b>, or "
                      "[the doc](https://link.example/c).", self.body)


if __name__ == "__main__":
    unittest.main()
