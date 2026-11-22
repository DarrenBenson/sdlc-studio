"""BG1125: the brief's UNIT DIFF holds the briefed unit's own commits, not every commit to its
Affects since the run's base.

The section was `git diff <base> HEAD -- <Affects>`, so when two units of one run changed the
same file, each unit's brief carried the other's hunks as if they were its own, and a reviewer
judged work it was not briefed on. When the commits since the base that change the unit's
Affects include commits naming it (in the subject or on a `Refs:` line, as the criteria runner
reads them) and commits that do not, the section now holds only its own, commit by commit, and
names the ones it left out. Each case drives `critic.py brief` against a throwaway repository
whose open run names both units.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402 - confined git for the fixture repo
import loader  # noqa: E402

critic = loader.load_script("critic")
SCRIPTS = loader.SCRIPTS_DIR
_STORY = ("# {uid}: a widget\n\n> **Status:** In Progress\n> **Affects:** src/a.py\n"
          "> **Points:** 2\n\n## Acceptance Criteria\n\n- [ ] **AC1** Given a widget, when it "
          "runs, then it returns one. Fails on: two\n  - **Verify:** shell true\n")
#: Thirty lines, so a change to lines 2, 12, 20 and 28 makes four hunks git keeps apart.
_LINES = [f"line{i} = {i}\n" for i in range(1, 31)]


def _set(root: Path, edits: dict[int, str]) -> None:
    lines = (root / "src" / "a.py").read_text(encoding="utf-8").splitlines(keepends=True)
    for number, text in edits.items():
        lines[number - 1] = f"{text}\n"
    (root / "src" / "a.py").write_text("".join(lines), encoding="utf-8")


def _commit(root: Path, message: str, edits: dict[int, str] | None = None) -> str:
    if edits:
        _set(root, edits)
    gitutil.git(["add", "-A"], root)
    gitutil.git(["commit", "-qm", message], root)
    return gitutil.git(["rev-parse", "HEAD"], root, text=True).stdout.strip()


def _project(root: Path) -> str:
    """US0001 and US0002 both declaring src/a.py, committed; the run's base is returned."""
    (root / "src").mkdir()
    (root / "src" / "a.py").write_text("".join(_LINES), encoding="utf-8")
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    for uid in ("US0001", "US0002"):
        (stories / f"{uid}-a-widget.md").write_text(_STORY.format(uid=uid), encoding="utf-8")
    (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
    gitutil.git(["init", "-q"], root)
    base = _commit(root, "base")
    state = root / "sdlc-studio" / ".local" / "run-state.json"
    state.parent.mkdir(parents=True)
    state.write_text(json.dumps({"schema": 1, "run_id": "RUN-A", "outcome": "running",
                                 "started_at": "2026-10-01T08:00:00Z",
                                 "batch": ["US0001", "US0002"], "base_ref": base}),
                     encoding="utf-8")
    return base


def _brief(root: Path, unit: str, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "critic.py"), "brief", "--unit", unit,
         "--seat", "qa", "--tier", "light", *argv, "--root", str(root)],
        capture_output=True, text=True, check=False, timeout=120, env=gitutil.git_env())


def _section(brief: str) -> tuple[str, list[str]]:
    """The UNIT DIFF heading's parenthesis and the section's lines after it."""
    m = re.search(r"(?m)^--- UNIT DIFF \(([^\n]*)\) ---\n", brief)
    assert m is not None, brief
    return m.group(1), brief[m.end():brief.index("\n\n", m.end())].split("\n")


def _added(lines: list[str]) -> list[str]:
    return [ln[1:] for ln in lines if ln.startswith("+") and not ln.startswith("+++")]


class UnitDiffOwnTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def _two_units(self) -> tuple[str, dict[str, str]]:
        root = self.root
        base = _project(root)
        shas = {"one": _commit(root, "feat(US0001): one", {2: "one = 1"}),
                "two": _commit(root, "feat(US0002): two", {12: "two = 2"})}
        # A run's records commit, naming no unit and changing no Affects file: never listed.
        (root / "notes.md").write_text("the run's notes\n", encoding="utf-8")
        shas["records"] = _commit(root, "docs(RUN-A): record the run")
        shas.update({"refs": _commit(root, "chore: a shared tidy\n\nRefs: US0001",
                                     {20: "refs = 1"}),
                     "three": _commit(root, "fix(US0001): three", {28: "three = 3"})})
        return base, shas

    def test_the_diff_holds_only_the_units_own_commits(self) -> None:
        """AC1. Mutants: the whole `git diff <base> HEAD` kept, carrying US0002's hunk in
        US0001's brief; a commit naming the unit only on a `Refs:` line left out; the commits
        listed newest first; the left-out commit unnamed; the commits read without the Affects
        pathspec, so the run's records commit, which changes no Affects file, is counted as
        left out. Each unit's brief holds its own hunks and none of the other's, and the
        left-out line reads in the singular for one commit and in the plural for three."""
        root = self.root
        base, shas = self._two_units()
        proc = _brief(root, "US0001")
        self.assertEqual(0, proc.returncode, proc.stderr)
        heading, lines = _section(proc.stdout)
        self.assertEqual(["one = 1", "refs = 1", "three = 3"], _added(lines), proc.stdout)
        self.assertNotIn("two = 2", proc.stdout)
        self.assertEqual(f"the 3 commits since {base} naming US0001: "
                         f"git diff <commit>^ <commit> -- src/a.py", heading)
        markers = [ln for ln in lines if ln.startswith("commit ")]
        self.assertEqual([f"commit {shas['one'][:12]} feat(US0001): one",
                          f"commit {shas['refs'][:12]} chore: a shared tidy",
                          f"commit {shas['three'][:12]} fix(US0001): three"], markers)
        # each commit's lines are its own diff against its parent, in order, whole
        expected: list[str] = []
        for key in ("one", "refs", "three"):
            sha = shas[key]
            expected.append(next(m for m in markers if sha[:12] in m))
            expected += gitutil.git(["diff", f"{sha}^", sha, "--", "src/a.py"], root,
                                    text=True).stdout.rstrip("\n").split("\n")
        self.assertEqual(expected, lines[:len(expected)])
        self.assertEqual([f"Left out: 1 commit since the base changes these files without "
                          f"naming US0001 in its subject or a Refs: line ({shas['two'][:12]}); "
                          f"git diff {base} HEAD -- src/a.py shows it with this unit's."],
                         lines[len(expected):])
        # the other unit's brief: its own hunk, none of US0001's
        proc = _brief(root, "US0002")
        self.assertEqual(0, proc.returncode, proc.stderr)
        heading, lines = _section(proc.stdout)
        self.assertEqual(["two = 2"], _added(lines))
        self.assertTrue(heading.startswith(f"the 1 commit since {base} naming US0002"), heading)
        self.assertIn(f"Left out: 3 commits since the base change these files without naming "
                      f"US0002 in their subject or a Refs: line ({shas['one'][:12]}, "
                      f"{shas['refs'][:12]}, {shas['three'][:12]}); git diff {base} HEAD -- "
                      f"src/a.py shows them with this unit's.", proc.stdout)
        self.assertNotIn(shas["records"][:12], proc.stdout)

    def test_a_range_of_only_the_units_commits_or_none_keeps_the_whole_diff(self) -> None:
        """The controls. Only the unit's commits change the file: the section is the whole
        `git diff <base> HEAD` under its heading, as before. No commit names the unit (a run
        whose commits name no id): the whole diff too, never an empty section. Mutant: the
        own-commit form taken whenever another commit exists, so the second case reads as no
        change at all. US0002 also commits a file outside the Affects, which counts neither as
        its own commit to them nor as one left out. Mutant: the commits read without the
        Affects pathspec, so US0001 takes the own-commit form and names US0002's commit as left
        out, and US0002 is handed its commit's empty diff."""
        root = self.root
        base = _project(root)
        _commit(root, "feat(US0001): one", {2: "one = 1"})
        (root / "src" / "b.py").write_text("b = 1\n", encoding="utf-8")
        _commit(root, "feat(US0002): b only")
        _commit(root, "fix(US0001): three", {28: "three = 3"})
        whole = gitutil.git(["diff", base, "HEAD", "--", "src/a.py"], root,
                            text=True).stdout.rstrip("\n").split("\n")
        for unit, added in (("US0001", ["one = 1", "three = 3"]),
                            ("US0002", ["one = 1", "three = 3"])):
            with self.subTest(unit=unit):
                proc = _brief(root, unit)
                self.assertEqual(0, proc.returncode, proc.stderr)
                heading, lines = _section(proc.stdout)
                self.assertEqual(f"git diff {base} HEAD -- src/a.py", heading)
                self.assertEqual(whole, lines)
                self.assertEqual(added, _added(lines))
                self.assertNotIn("Left out:", proc.stdout)

    def test_the_cap_holds_in_the_own_commit_form(self) -> None:
        """The tier's line cap holds over the commits as over the range: past it, the remainder
        names each file cut, at the commit it was cut in, with the command that prints it.
        Mutant: the cap reset per commit, so the section runs past it."""
        root = self.root
        base, shas = self._two_units()
        with unittest.mock.patch.dict(critic.BRIEF_DIFF_LINES, {"light": 12}), \
                unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True):
            text = critic.brief(root, "US0001", "qa", "light")
        _heading, lines = _section(text)
        self.assertEqual(14, len(lines), lines)
        three = shas["three"][:12]
        refs = shas["refs"][:12]
        self.assertRegex(lines[12], r"^Diff cut at the 12-line cap for the light tier "
                                    r"\(review\.brief_diff_lines\)\. Not shown: ")
        self.assertIn(f"(git diff {three}^ {three} -- src/a.py)", lines[12])
        self.assertIn(f"(git diff {refs}^ {refs} -- src/a.py)", lines[12])
        self.assertNotIn("two = 2", text)
        self.assertTrue(lines[13].startswith("Left out: 1 commit"), lines[13])

    def test_commits_git_cannot_list_are_said(self) -> None:
        """The unit's commits unreadable: the section says git could not take the diff, never
        falls back to a diff carrying the other unit's hunks. Mutant: the failure swallowed."""
        root = self.root
        self._two_units()
        import verify_ac  # noqa: PLC0415 - the sibling the brief reads the unit's commits through
        failing = verify_ac.CoverageUnavailable("git could not list base..HEAD: ['fatal: x']")
        with unittest.mock.patch.object(verify_ac, "_unit_commit_shas", side_effect=failing), \
                unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True):
            text = critic.brief(root, "US0001", "qa", "light")
        _heading, lines = _section(text)
        self.assertEqual(["(git could not take this diff: git could not list base..HEAD: "
                          "['fatal: x'])"], lines)


if __name__ == "__main__":
    unittest.main()
