"""BG0970: `critic.py brief` names the unit's uncommitted Affects and the commit it was cut at.

The brief sends the reviewer to an isolated checkout, which in Claude Code is a worktree made
from HEAD. When the author has not committed the unit's change, that worktree holds the code
before it, and the reviewer judges the wrong revision with no sign of it. The brief now names
each Affects path with an uncommitted change on stderr, saying an isolated reviewer will not see
it, says nothing over a clean tree, and records the commit it was cut at in its note and its
footer, so a verdict can be matched to the revision it judged.

Each case drives the shipped `critic.py brief` against a throwaway git repository, with git
confined to the fixture; the git failure case runs the verb in-process with git stubbed.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
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
NOTES = Path("sdlc-studio") / ".local" / "briefs.jsonl"
#: the words the warning carries, and the absence a clean tree is held to
UNSEEN = "an isolated reviewer will not see"
AFFECTS = "src/a.py, src/new.py, src/pkg/, sdlc-studio/reviews/"
PRIOR = "VERDICT: REJECT\nISSUES: [new] a is wrong\nBLOCKING: [new] a is wrong\n"


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _project(root: Path, repo: bool = True) -> None:
    """US0001 declaring a file, a file not yet written, a directory and the review ledgers'
    directory; one undeclared file beside them; (with `repo`) one commit holding it all."""
    for rel in ("src/a.py", "src/c.py", "src/pkg/m.py"):
        _write(root, rel, "x = 1\n")
    _write(root, "sdlc-studio/reviews/critic-verdicts.md", "# Critic Verdicts\n")
    _write(root, "sdlc-studio/stories/US0001-the-widget.md",
           f"# US0001: the widget\n\n> **Status:** In Progress\n> **Affects:** {AFFECTS}\n"
           "> **Points:** 2\n\n## Acceptance Criteria\n\n- [ ] **AC1** it works\n"
           "  - **Verify:** shell true\n")
    _write(root, ".gitignore", "sdlc-studio/.local/\n")
    if repo:
        gitutil.git(["init", "-q"], root)
        _commit(root, "base")


def _commit(root: Path, message: str) -> str:
    gitutil.git(["add", "-A"], root)
    gitutil.git(["commit", "-qm", message], root)
    return gitutil.git(["rev-parse", "--short=12", "HEAD"], root, text=True).stdout.strip()


def _brief(root: Path, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "critic.py"), "brief", "--unit", "US0001",
         "--seat", "qa", "--tier", "light", *argv, "--root", str(root)],
        capture_output=True, text=True, check=False, timeout=120, env=gitutil.git_env())


def _warning(stderr: str) -> str:
    """The stderr line carrying the uncommitted-Affects warning, or ""."""
    return next((line for line in stderr.splitlines() if UNSEEN in line), "")


def _named(stderr: str) -> list[str]:
    """The paths the warning names, in its order, or none when there is no warning."""
    line = _warning(stderr)
    return line.split(f"{UNSEEN}: ", 1)[1].split(". A reviewer's", 1)[0].split(", ") if line else []


def _notes(root: Path) -> list[dict]:
    return [json.loads(line) for line in
            (root / NOTES).read_text(encoding="utf-8").splitlines() if line.strip()]


class UncommittedAffectsTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def test_brief_warns_on_uncommitted_affects(self) -> None:
        """AC1. Mutants: the check dropped; untracked files left out (the new file unnamed); a
        declared directory's members left out; the undeclared file named; the warning sent to
        stdout, where it would join the brief and move its fingerprint; the rejoinder brief
        left unchecked."""
        root = self.root
        _project(root)
        _write(root, "src/a.py", "x = 2\n")
        _write(root, "src/new.py", "y = 1\n")
        _write(root, "src/pkg/m.py", "x = 3\n")
        _write(root, "src/c.py", "x = 4\n")
        proc = _brief(root)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertTrue(proc.stdout.strip(), "the warning refused the brief")
        line = _warning(proc.stderr)
        self.assertTrue(line, f"no warning on stderr:\n{proc.stderr}")
        for rel in ("src/a.py", "src/new.py", "src/pkg/m.py"):
            self.assertIn(rel, line)
        self.assertIn("uncommitted", line)
        self.assertNotIn("src/c.py", line, "an undeclared file is not the unit's")
        self.assertNotIn(UNSEEN, proc.stdout, "the warning reached the brief itself")
        prior = root / "prior.txt"
        prior.write_text(PRIOR, encoding="utf-8")
        again = _brief(root, "--rejoinder", str(prior))
        self.assertEqual(0, again.returncode, again.stderr)
        self.assertIn("src/a.py", _warning(again.stderr), "the re-review brief said nothing")

    def test_brief_warns_on_uncommitted_affects_staged_deleted_or_renamed(self) -> None:
        """AC1's other states, each named by its own path: a staged edit, a staged deletion, a
        staged rename (both of its paths), a deletion not staged, and a new file in a new
        directory beneath a declared one. Mutants: only entries with a worktree change kept (the
        staged ones unnamed); only paths still on disk kept (the deletions unnamed); renames
        detected, so the rename record's second path is misread; untracked directories named
        in place of their files."""
        root = self.root
        for rel in ("src/pkg/staged.py", "src/pkg/gone.py", "src/pkg/old.py"):
            _write(root, rel, "x = 1\n")
        _project(root)
        _write(root, "src/pkg/staged.py", "x = 2\n")
        gitutil.git(["add", "src/pkg/staged.py"], root)
        gitutil.git(["rm", "-q", "src/pkg/gone.py"], root)
        gitutil.git(["mv", "src/pkg/old.py", "src/pkg/renamed.py"], root)
        (root / "src" / "a.py").unlink()
        _write(root, "src/pkg/sub/x.py", "y = 1\n")
        proc = _brief(root)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(["src/a.py", "src/pkg/gone.py", "src/pkg/old.py", "src/pkg/renamed.py",
                          "src/pkg/staged.py", "src/pkg/sub/x.py"], _named(proc.stderr),
                         proc.stderr)

    def test_brief_warns_on_uncommitted_affects_in_a_project_below_the_repository_top(self):
        """A project whose root is a directory of its repository: git names each path from the
        repository's top, and the warning names it from the root, as the Affects do, and still
        leaves out the review ledger's append and the verdict file the brief issued. Mutant:
        the root's prefix left on, so `proj/src/a.py` is named and the tooling's writes are not
        recognised."""
        top = self.root
        root = top / "proj"
        _project(root, repo=False)
        gitutil.git(["init", "-q"], top)
        _commit(top, "base")
        _write(root, "src/a.py", "x = 2\n")
        proc = _brief(root)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(["src/a.py"], _named(proc.stderr), proc.stderr)
        _commit(top, "a moves")
        issued = Path(_notes(root)[-1]["verdict_file"])
        self.assertTrue(issued.is_relative_to(root.resolve()), "premise: issued in the project")
        issued.write_text(PRIOR, encoding="utf-8")
        _write(root, "sdlc-studio/reviews/critic-verdicts.md", "# Critic Verdicts\n\nrow\n")
        again = _brief(root, "--rejoinder", str(issued))
        self.assertEqual(0, again.returncode, again.stderr)
        self.assertEqual([], _named(again.stderr), again.stderr)

    def test_brief_on_a_clean_tree_is_silent_after_a_verdict_is_written(self) -> None:
        """The verdict file a reviewer writes at the path the brief issued is not the unit's
        change, under a unit declaring the reviews directory, so the re-review brief over it
        names nothing. Mutant: the verdict files named as uncommitted Affects. The positive
        control: any other new file under the declared directory, one whose name merely starts
        with `verdicts` among them, is still named."""
        root = self.root
        _project(root)
        proc = _brief(root)
        self.assertEqual(0, proc.returncode, proc.stderr)
        issued = Path(_notes(root)[-1]["verdict_file"])
        self.assertTrue(issued.is_relative_to(root.resolve() / "sdlc-studio" / "reviews"),
                        "premise: the verdict file is issued under the declared directory")
        issued.write_text(PRIOR, encoding="utf-8")
        again = _brief(root, "--rejoinder", str(issued))
        self.assertEqual(0, again.returncode, again.stderr)
        self.assertEqual("", _warning(again.stderr), again.stderr)
        _write(root, "sdlc-studio/reviews/verdicts.md", "x\n")
        proc = _brief(root, "--rejoinder", str(issued))
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(["sdlc-studio/reviews/verdicts.md"], _named(proc.stderr), proc.stderr)

    def test_brief_on_a_clean_tree_is_silent(self) -> None:
        """AC2. Mutants: a warning printed whatever git says; an undeclared file's edit read as
        the unit's; the review ledger's own append (an uncommitted write under a declared
        directory that no unit's change is made of) named as the unit's; a git status git
        could not give read as a clean tree."""
        root = self.root
        _project(root)
        proc = _brief(root)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual("", _warning(proc.stderr), proc.stderr)
        _write(root, "src/c.py", "x = 4\n")
        _write(root, "sdlc-studio/reviews/critic-verdicts.md", "# Critic Verdicts\n\nrow\n")
        proc = _brief(root)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual("", _warning(proc.stderr), proc.stderr)
        # git that cannot give a status is said, never read as a clean tree
        real = critic._git

        def broken(at, *args):
            if args[:1] == ("status",):
                return subprocess.CompletedProcess([], 128, b"", b"fatal: index file corrupt\n")
            return real(at, *args)

        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True), \
                unittest.mock.patch.object(critic, "_git", broken), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = critic.main(["brief", "--unit", "US0001", "--seat", "qa", "--tier", "light",
                              "--root", str(root)])
        self.assertEqual(0, rc, err.getvalue())
        self.assertIn("could not read git status (fatal: index file corrupt)", err.getvalue())
        self.assertIn("cannot say whether US0001's Affects hold uncommitted", err.getvalue())

    def test_brief_records_its_commit(self) -> None:
        """AC3. Mutants: no commit in the note; the footer line dropped; the commit read once
        and kept, so a later brief names an earlier revision; the re-review brief naming none;
        a commit invented outside a repository."""
        root = self.root
        _project(root)
        head = gitutil.git(["rev-parse", "--short=12", "HEAD"], root, text=True).stdout.strip()
        proc = _brief(root)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(head, _notes(root)[-1]["commit"])
        self.assertIn(f"\nbrief cut at commit: {head}\n", proc.stderr)
        fp = _notes(root)[-1]["fp"]
        # the commit line sits straight beneath the fingerprint line, as the changelog says
        self.assertIn(f"brief fingerprint: {fp}\nbrief cut at commit: {head}\n", proc.stderr)
        _write(root, "src/a.py", "x = 2\n")
        later = _commit(root, "a moves")
        self.assertNotEqual(head, later)
        proc = _brief(root)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(later, _notes(root)[-1]["commit"])
        self.assertIn(f"brief cut at commit: {later}", proc.stderr)
        # the re-review brief names its commit the same way
        prior = root / "prior.txt"
        prior.write_text(PRIOR, encoding="utf-8")
        proc = _brief(root, "--rejoinder", str(prior))
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertTrue(_notes(root)[-1]["rejoinder"], "premise: the note is the re-review's")
        self.assertEqual(later, _notes(root)[-1]["commit"])
        self.assertIn(f"brief fingerprint: {_notes(root)[-1]['fp']}\nbrief cut at commit: "
                      f"{later}\n", proc.stderr)
        # outside a repository there is no commit to name, and none is claimed
        with tempfile.TemporaryDirectory() as d:
            bare = Path(d)
            _project(bare, repo=False)
            proc = _brief(bare)
            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertNotIn("commit", _notes(bare)[-1])
            self.assertNotIn("brief cut at commit", proc.stderr)
            self.assertEqual("", _warning(proc.stderr), "no repository, no uncommitted change")
            self.assertNotIn("could not read git status", proc.stderr)


if __name__ == "__main__":
    unittest.main()
