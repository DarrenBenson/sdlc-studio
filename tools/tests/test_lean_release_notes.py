"""US0898: a shipped release's notes stay as shipped, and the defect count is written at the cut.

`ReleaseNotesClaimTests` and the live-page cases of `KnownIssuesPageTests` compared a published
record with the live bug corpus on every run, so filing or closing any finding turned the suite
red until somebody hand-edited the notes of a release that had already shipped (33 edits to the
v5.1.0 notes, 99 to the known-issues page). The count is now written once, by
`known_issues.py write --release <version>` at the cut, and the page is checked against the corpus
at the tag only, by `.githooks/pre-push`, at the tagged commit. Every fixture here is a throwaway
directory.
"""
# test-census-subject: tools/known_issues.py
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import known_issues as ki  # noqa: E402
# Imported as a MODULE so unittest does not collect and re-run its cases here.
import test_pre_push_hook as _pp  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "tools" / "known_issues.py"

#: What a tools test must name to read the corpus's disclosure set, the page or a release's notes.
#: Selection is DERIVED from these rather than listed, so a module added later that compares a
#: published record with the corpus - by path, or through the generator - runs here unnamed.
READERS = ("known_issues", "known-issues.md", "release-notes-v")


def _env() -> dict:
    """The caller's environment minus every git locating variable, so nothing a hook handed the
    suite steers a fixture at the outer repository."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _finding(root: Path, bug_id: str, status: str, severity: str, title: str = "a finding") -> None:
    bugs = root / ki.BUGS_REL
    bugs.mkdir(parents=True, exist_ok=True)
    (bugs / f"{bug_id}-x.md").write_text(
        f"# {bug_id}: {title}\n\n> **Status:** {status}\n> **Severity:** {severity}\n",
        encoding="utf-8")


def _cli(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPT), *args, "--root", str(root)],
                          capture_output=True, text=True, timeout=120, check=False, env=_env())


def _copy_repository(dest: Path) -> None:
    """Every file this checkout tracks or would track, as it stands in the working tree."""
    listed = _pp._git(REPO, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    for rel in filter(None, listed.stdout.split("\0")):
        src = REPO / rel
        if not src.is_file():
            continue                      # deleted in the working tree, or a submodule
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest / rel, follow_symlinks=False)


def _hook_lines(stderr: str) -> list[str]:
    return [ln for ln in stderr.splitlines() if ln.startswith("pre-push:")]


class FrozenNotesTests(unittest.TestCase):

    def test_filing_a_finding_reddens_no_test(self) -> None:
        """AC1. MUTANTS: (1) restore `ReleaseNotesClaimTests`; (2) restore the byte-identity case
        of `KnownIssuesPageTests`; (3) a new module asserting `ki.main(["check"]) == 0`, a live
        comparison naming neither published path."""
        own = Path(__file__).name
        readers = sorted(p.stem for p in (REPO / "tools" / "tests").glob("test_*.py")
                         if p.name != own
                         and any(r in p.read_text(encoding="utf-8") for r in READERS))
        self.assertIn("test_known_issues", readers,
                      f"the selection found no module reading the page or the notes: {readers}")
        with tempfile.TemporaryDirectory() as d:
            copy = Path(d) / "repo"
            _copy_repository(copy)
            ids = [int(p.name[2:6]) for p in (copy / ki.BUGS_REL).glob("BG[0-9][0-9][0-9][0-9]*.md")]
            new = f"BG{max(ids) + 1:04d}"
            _finding(copy, new, "Open", "Medium", "one extra finding, filed and nothing else changed")
            self.assertIn(new, ki.corpus(copy),
                          "the extra finding is invisible to the generator, so it proves nothing")
            r = subprocess.run([sys.executable, "-B", "-m", "unittest", "-q", *readers],
                               cwd=copy / "tools" / "tests", capture_output=True, text=True,
                               timeout=600, check=False,
                               env={**_env(), "PYTHONDONTWRITEBYTECODE": "1"})
            self.assertEqual(0, r.returncode,
                             f"filing {new} turned the tools suite red ({readers}):\n"
                             f"{r.stderr[-4000:]}")

    def test_the_cut_writes_the_page_and_only_the_untagged_notes(self) -> None:
        """AC2. MUTANTS: (1) write the page only, leaving the notes' sentence stale; (2) count Low
        as Medium; (3) drop the tag refusal, so a shipped release's notes are rewritten; (4) write
        the page before refusing a tagged version; (5) rewrite the notes' prose beyond the line."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            docs = root / "docs"
            docs.mkdir(parents=True)
            _pp._git(root, "init", "-q", "-b", "main", str(root))
            _finding(root, "BG0001", "Open", "Medium")
            _finding(root, "BG0002", "Open", "Low")
            _finding(root, "BG0003", "Open", "High")
            _finding(root, "BG0004", "Fixed", "Medium")
            _finding(root, "BG0006", "Open", "Medium")    # two Mediums, one Low: a swap shows
            shipped = docs / "release-notes-v9.0.0.md"
            shipped.write_text("# v9.0.0\n\n**v9.0.0 discloses 5 open defects: 5 Medium, 0 Low.**\n\n"
                               "What v9.0.0 shipped with.\n", encoding="utf-8")
            _pp._git(root, "add", "-A")
            _pp._git(root, "commit", "-q", "-m", "v9.0.0")
            _pp._git(root, "tag", "v9.0.0")
            cut = docs / "release-notes-v9.1.0.md"
            cut.write_text("# v9.1.0\n\nIntro.\n\n**v9.1.0 discloses 0 open defects: 0 Medium, "
                           "0 Low.**\n\nTail prose.\n", encoding="utf-8")

            r = _cli(root, "write", "--release", "9.1.0")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertEqual(ki.render(root, "9.1.0"),
                             (docs / "known-issues.md").read_text(encoding="utf-8"))
            self.assertEqual("# v9.1.0\n\nIntro.\n\n**v9.1.0 discloses 3 open defects: 2 Medium, "
                             "1 Low.**\n\nTail prose.\n", cut.read_text(encoding="utf-8"))
            self.assertEqual(0, _cli(root, "check").returncode, "the page just written disagrees")

            # A tagged version is refused, and nothing is written: the corpus has moved, so any
            # write at all would show.
            _finding(root, "BG0005", "Open", "Medium")
            page_before = (docs / "known-issues.md").read_bytes()
            notes_before = shipped.read_bytes()
            refused = _cli(root, "write", "--release", "v9.0.0")
            self.assertNotEqual(0, refused.returncode, "a tagged release's notes were rewritten")
            self.assertIn("v9.0.0", refused.stderr)
            self.assertIn("tag", refused.stderr)
            self.assertEqual(notes_before, shipped.read_bytes(), "the shipped notes moved")
            self.assertEqual(page_before, (docs / "known-issues.md").read_bytes(),
                             "a refused cut still rewrote the page")

    def test_the_cut_refuses_what_it_cannot_write(self) -> None:
        """MUTANTS: (1) drop the one-count-line guard, so notes with no line report `wrote` while
        untouched; (2) accept two count lines and rewrite both; (3) drop the missing-notes refusal;
        (4) read `_tagged`'s None (git cannot say) as "not tagged"."""
        with tempfile.TemporaryDirectory() as d:
            # Not a repository: git cannot say whether the version is tagged, so the cut fails
            # closed rather than reading silence as "untagged".
            bare = Path(d) / "bare"
            (bare / "docs").mkdir(parents=True)
            _finding(bare, "BG0001", "Open", "Medium")
            (bare / "docs" / "release-notes-v9.1.0.md").write_text(
                "**v9.1.0 discloses 0 open defects: 0 Medium, 0 Low.**\n", encoding="utf-8")
            r = _cli(bare, "write", "--release", "9.1.0")
            self.assertNotEqual(0, r.returncode, "an unreadable tag list was read as untagged")
            self.assertIn("cannot tell whether v9.1.0 is tagged", r.stderr)
            self.assertFalse((bare / ki.PAGE_REL).exists(), "a refused cut wrote the page")

            root = Path(d) / "repo"
            (root / "docs").mkdir(parents=True)
            _pp._git(root, "init", "-q", "-b", "main", str(root))
            _finding(root, "BG0001", "Open", "Medium")
            notes = root / "docs" / "release-notes-v9.1.0.md"
            missing = _cli(root, "write", "--release", "9.1.0")
            self.assertNotEqual(0, missing.returncode)
            self.assertIn("release-notes-v9.1.0.md does not exist", missing.stderr)
            for body in ("# v9.1.0\n\nNo count line at all.\n",
                         "**v9.1.0 discloses 0 open defects: 0 Medium, 0 Low.**\n\n"
                         "**v9.1.0 discloses 0 open defects: 0 Medium, 0 Low.**\n"):
                notes.write_text(body, encoding="utf-8")
                r = _cli(root, "write", "--release", "9.1.0")
                self.assertNotEqual(0, r.returncode, f"notes reading {body!r} were accepted")
                self.assertIn("exactly one line", r.stderr)
                self.assertNotIn("wrote", r.stdout)
                self.assertEqual(body, notes.read_text(encoding="utf-8"))
            self.assertFalse((root / ki.PAGE_REL).exists(), "a refused cut wrote the page")

    def test_the_page_is_checked_at_the_tag_only(self) -> None:
        """AC3. MUTANTS: (1) run the check at a branch push too; (2) drop the check from the tag
        push; (3) an or-true fallback, so the check's exit code never refuses; (4) a hook refusal
        line that does not name `known_issues.py write`; (5) judge the working tree rather than the
        tagged commit, so a fresh page left uncommitted lets a stale tagged page ship."""
        fx = _pp._Clone()
        try:
            _finding(fx.clone, "BG0001", "Open", "Medium")
            _pp._git(fx.clone, "add", "-A")
            _pp._git(fx.clone, "commit", "-q", "-m", "file a finding; the page now disagrees")
            self.assertEqual(1, _cli(fx.clone, "check").returncode, "the fixture page agrees")

            branch = fx.push()
            self.assertEqual(0, branch.returncode, "a branch push ran the page check:\n" + branch.stderr)
            self.assertNotIn("known_issues.py", branch.stderr)
            self.assertEqual(["--boundary push"], fx.gate_calls())

            _pp._git(fx.clone, "tag", "v0.0.1")
            tag = fx.push("v0.0.1")
            self.assertNotEqual(0, tag.returncode, "a tag whose page disagrees was pushed")
            self.assertTrue(any("known_issues.py write --release" in ln and "disagrees" in ln
                                for ln in _hook_lines(tag.stderr)),
                            "the hook's own refusal does not name the cut:\n" + tag.stderr)
            self.assertNotIn("v0.0.1", _pp._git(fx.remote, "tag", "-l").stdout)
            self.assertEqual(["--boundary push"], fx.gate_calls(),
                             "the gate ran after the cheap page check had already refused")

            # The reviewer's probe: the page is cut but left UNCOMMITTED, and the stale tag is
            # pushed again. The working tree agrees; the tag does not, and the tag is what ships.
            (fx.clone / ki.PAGE_REL).write_text(ki.render(fx.clone, "6.0.0"), encoding="utf-8")
            self.assertEqual(0, _cli(fx.clone, "check").returncode, "the working tree disagrees")
            uncommitted = fx.push("v0.0.1")
            self.assertNotEqual(0, uncommitted.returncode,
                                "a tag carrying a stale page shipped because the working tree agreed")
            self.assertNotIn("v0.0.1", _pp._git(fx.remote, "tag", "-l").stdout)

            # The positive control: the page committed and a tag on that commit goes through.
            _pp._git(fx.clone, "add", "-A")
            _pp._git(fx.clone, "commit", "-q", "-m", "cut the page")
            _pp._git(fx.clone, "tag", "v0.0.2")
            ok = fx.push("v0.0.2")
            self.assertEqual(0, ok.returncode, ok.stderr)
            self.assertEqual("--boundary release", fx.gate_calls()[-1])
        finally:
            fx.cleanup()

    def test_a_check_that_cannot_run_is_reported_as_such(self) -> None:
        """MUTANTS: (1) the hook reads every non-zero exit as a disagreement; (2) the checker lets
        a crash exit 1, the code that means "disagrees"; (3) a crash lets the tag through."""
        fx = _pp._Clone()
        try:
            script = fx.clone / "tools" / "known_issues.py"
            text = script.read_text(encoding="utf-8")
            anchor = 'if __name__ == "__main__":'
            self.assertEqual(1, text.count(anchor))
            script.write_text(text.replace(anchor, 'def _check(root):\n    raise RuntimeError('
                                           '"simulated crash")\n\n\n' + anchor), encoding="utf-8")
            _pp._git(fx.clone, "tag", "v0.0.1")
            r = fx.push("v0.0.1")
            self.assertNotEqual(0, r.returncode, "a check that crashed let the tag through")
            self.assertIn("simulated crash", r.stderr, "the crash itself was not shown")
            lines = _hook_lines(r.stderr)
            self.assertTrue(any("could not run" in ln for ln in lines), r.stderr)
            self.assertFalse(any("disagrees" in ln for ln in lines),
                             "a crash was reported as a disagreement:\n" + r.stderr)
            self.assertEqual([], fx.gate_calls())
        finally:
            fx.cleanup()


if __name__ == "__main__":
    unittest.main()
