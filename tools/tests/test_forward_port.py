"""tools/forward-port.sh - the dev-repo rsync to the installed copy, guarded (RED first).

The forward-port was hand-typed four times in one day; a wrong --delete without the
.local exclude destroys the installed copy's local state, and BG0100 records what a
wrong direction does. The script wraps the canonical rsync: dry-run by default,
--yes to apply, wrong direction or a non-dev-repo cwd refused loudly.
"""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO / "tools" / "forward-port.sh"


def _fake_dev_repo(root: pathlib.Path) -> pathlib.Path:
    """A hermetic dev-repo shape: the structural markers the guard checks, a skill
    tree with content, and the two exclusions that must never be copied."""
    (root / "tools").mkdir(parents=True)
    shutil.copy(SCRIPT, root / "tools" / "forward-port.sh")
    skill = root / ".claude" / "skills" / "sdlc-studio"
    (skill / "scripts" / "__pycache__").mkdir(parents=True)
    (skill / ".local").mkdir()
    (skill / "SKILL.md").write_text("# skill\n", encoding="utf-8")
    (skill / "scripts" / "a.py").write_text("x = 1\n", encoding="utf-8")
    (skill / "scripts" / "__pycache__" / "a.pyc").write_text("junk", encoding="utf-8")
    (skill / ".local" / "state.json").write_text("{}", encoding="utf-8")
    return root


def _run(cwd: pathlib.Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(cwd / "tools" / "forward-port.sh"), *args],
                          cwd=cwd, capture_output=True, text=True)


class ForwardPortTests(unittest.TestCase):
    def test_non_dev_repo_cwd_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / "tools").mkdir()
            shutil.copy(SCRIPT, root / "tools" / "forward-port.sh")   # script alone, no skill tree
            r = _run(root, "--target", d + "/elsewhere")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("dev repo", r.stderr)

    def test_reversed_direction_refused(self) -> None:
        # A target inside the repo is the BG0100 direction: the sweep would clobber
        # the git-tracked working tree.
        with tempfile.TemporaryDirectory() as d:
            root = _fake_dev_repo(pathlib.Path(d))
            r = _run(root, "--target", str(root / ".claude" / "skills" / "sdlc-studio"))
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("inside", r.stderr.lower())

    def test_dry_run_is_the_default(self) -> None:
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as t:
            root = _fake_dev_repo(pathlib.Path(d))
            target = pathlib.Path(t) / "installed"
            r = _run(root, "--target", str(target))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertFalse((target / "SKILL.md").exists())   # nothing written
            self.assertIn("--yes", r.stdout)                   # the apply path, named

    def test_yes_applies_with_the_exact_exclusions(self) -> None:
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as t:
            root = _fake_dev_repo(pathlib.Path(d))
            target = pathlib.Path(t) / "installed"
            target.mkdir()
            # pre-existing local state at the target MUST survive the --delete sweep
            (target / ".local").mkdir()
            (target / ".local" / "keep.json").write_text("{}", encoding="utf-8")
            (target / "stale.md").write_text("old\n", encoding="utf-8")
            r = _run(root, "--target", str(target), "--yes")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue((target / "SKILL.md").is_file())            # synced
            self.assertTrue((target / "scripts" / "a.py").is_file())
            self.assertFalse((target / "stale.md").exists())            # --delete swept
            self.assertTrue((target / ".local" / "keep.json").is_file())  # exclusion held
            self.assertFalse((target / "scripts" / "__pycache__").exists())

    def test_repo_root_itself_refused_as_target(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _fake_dev_repo(pathlib.Path(d))
            r = _run(root, "--target", str(root))
            self.assertNotEqual(r.returncode, 0)

    def test_leaf_symlink_into_the_repo_refused(self) -> None:
        # A symlink LEAF pointing inside the repo must resolve and refuse - an
        # unresolved leaf let the --delete sweep destroy repo contents.
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as t:
            root = _fake_dev_repo(pathlib.Path(d))
            (root / "precious").mkdir()
            (root / "precious" / "keep.txt").write_text("x", encoding="utf-8")
            link = pathlib.Path(t) / "innocent-name"
            link.symlink_to(root / "precious")
            r = _run(root, "--target", str(link), "--yes")
            self.assertNotEqual(r.returncode, 0)
            self.assertTrue((root / "precious" / "keep.txt").is_file())  # untouched

    def test_parent_of_repo_refused(self) -> None:
        # A target CONTAINING the repo is the other destructive direction: the
        # --delete sweep would remove the repo itself as extraneous.
        with tempfile.TemporaryDirectory() as d:
            parent = pathlib.Path(d)
            root = _fake_dev_repo(parent / "repo")
            r = _run(root, "--target", str(parent), "--yes")
            self.assertNotEqual(r.returncode, 0)
            self.assertTrue((root / "tools" / "forward-port.sh").is_file())  # survived

    def test_refused_run_creates_nothing_on_disk(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _fake_dev_repo(pathlib.Path(d))
            r = _run(root, "--target", str(root / "newdir" / "deeper"))
            self.assertNotEqual(r.returncode, 0)
            self.assertFalse((root / "newdir").exists())   # no mkdir side effect

    def test_dangling_symlink_target_refused_explicitly(self) -> None:
        # Unresolvable = unvouchable: the guard refuses by decision, not by a
        # downstream mkdir accident with a raw error.
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as t:
            root = _fake_dev_repo(pathlib.Path(d))
            link = pathlib.Path(t) / "dangling"
            link.symlink_to(pathlib.Path(t) / "nowhere")
            r = _run(root, "--target", str(link), "--yes")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("dangling", r.stderr)

    def test_existing_non_directory_target_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as t:
            root = _fake_dev_repo(pathlib.Path(d))
            f = pathlib.Path(t) / "a-file"
            f.write_text("x", encoding="utf-8")
            r = _run(root, "--target", str(f), "--yes")
            self.assertNotEqual(r.returncode, 0)


def _mirror_target(root: pathlib.Path, target: pathlib.Path) -> None:
    """The target as a faithful mirror of `_fake_dev_repo`'s skill tree: exactly the
    files the rsync would place, and none of the excluded ones."""
    (target / "scripts").mkdir(parents=True)
    (target / "SKILL.md").write_text("# skill\n", encoding="utf-8")
    (target / "scripts" / "a.py").write_text("x = 1\n", encoding="utf-8")


def _check_count(stdout: str) -> int:
    """The differing-file count the check printed, as an integer."""
    m = re.search(r"(\d+) file\(s\) differ", stdout)
    if not m:
        raise AssertionError(f"the check printed no differing-file count:\n{stdout}")
    return int(m.group(1))


def _listed_paths(stdout: str) -> set[str]:
    """The itemised paths, one per rsync line: an 11-char itemise flag (or `*deleting`)
    then the path at column 13."""
    return {line[12:].strip() for line in stdout.splitlines()
            if re.match(r"^(\*deleting|[<>ch.][fdLDS])", line)}


class DriftCheckTests(unittest.TestCase):
    """`--check`: the installed copy has drifted, and by how many files (US0388).

    The window between a fix landing in the repo and the mirror running is a window in
    which every other project on the machine still loads the old code. Nothing reported
    it, so the only defence was the operator remembering to ask.
    """

    def test_check_exits_non_zero_and_names_the_differing_file_count(self) -> None:
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as t:
            root = _fake_dev_repo(pathlib.Path(d))
            target = pathlib.Path(t) / "installed"
            _mirror_target(root, target)
            skill = root / ".claude/skills/sdlc-studio"
            # Five drifting FILES and nothing else: one changed, two absent from the
            # target (one of them inside a directory the target does not have), two
            # extra at the target (one of them inside a directory the repo does not
            # have). Every other path matches byte for byte.
            (target / "SKILL.md").write_text("# stale skill\n", encoding="utf-8")
            (skill / "NEW.md").write_text("new\n", encoding="utf-8")
            (skill / "newdir").mkdir()
            (skill / "newdir" / "three.md").write_text("three\n", encoding="utf-8")
            (target / "stale.md").write_text("old\n", encoding="utf-8")
            (target / "gonedir").mkdir()
            (target / "gonedir" / "gone.md").write_text("gone\n", encoding="utf-8")

            r = _run(root, "--check", "--target", str(target))

            self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
            # The two directories rsync also itemises (`cd+++++++++ newdir/` and
            # `*deleting gonedir/`) are consequences of the files inside them. Counting
            # them would inflate the number the operator is asked to act on, so the
            # count is 5 and not the 7 raw itemised lines.
            self.assertEqual(_check_count(r.stdout), 5,
                             f"five FILES differ; the check said otherwise:\n{r.stdout}")
            self.assertEqual(_listed_paths(r.stdout),
                             {"SKILL.md", "NEW.md", "newdir/three.md",
                              "stale.md", "gonedir/gone.md"})
            self.assertNotIn("newdir/\n", r.stdout)
            self.assertNotIn("gonedir/\n", r.stdout)
            # A check writes nothing: the drift it just reported must still be there.
            self.assertEqual((target / "SKILL.md").read_text(encoding="utf-8"),
                             "# stale skill\n")
            self.assertTrue((target / "stale.md").is_file())
            self.assertTrue((target / "gonedir" / "gone.md").is_file())
            self.assertFalse((target / "NEW.md").exists())
            self.assertFalse((target / "newdir").exists())

    def test_an_identical_target_is_in_sync_and_local_state_is_not_drift(self) -> None:
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as t:
            root = _fake_dev_repo(pathlib.Path(d))
            target = pathlib.Path(t) / "installed"
            _mirror_target(root, target)
            # The consuming copy's own state and the caches a run leaves behind. None of
            # it is drift: the check honours the exclusions the mirror honours.
            (target / ".local").mkdir()
            (target / ".local" / "state.json").write_text('{"different": true}',
                                                          encoding="utf-8")
            (target / "scripts" / "__pycache__").mkdir()
            (target / "scripts" / "__pycache__" / "a.pyc").write_text("junk",
                                                                     encoding="utf-8")
            (target / ".pytest_cache").mkdir()
            (target / ".pytest_cache" / "CACHEDIR.TAG").write_text("x", encoding="utf-8")

            r = _run(root, "--check", "--target", str(target))

            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(_listed_paths(r.stdout), set(),
                             f"nothing should be itemised:\n{r.stdout}")
            self.assertIn("in sync", r.stdout)
            # The exclusions are preserved, not swept, and nothing was written.
            self.assertEqual((target / ".local" / "state.json").read_text(encoding="utf-8"),
                             '{"different": true}')
            self.assertTrue((target / "scripts" / "__pycache__" / "a.pyc").is_file())

    def test_an_absent_or_pinned_copy_is_reported_and_does_not_fail(self) -> None:
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as t:
            root = _fake_dev_repo(pathlib.Path(d))

            absent = pathlib.Path(t) / "never-installed"
            r = _run(root, "--check", "--target", str(absent))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("no installed copy", r.stdout)
            self.assertFalse(absent.exists(), "a check must not create the target")

            # A pinned copy that IS drifted. Without the marker the same target fails,
            # so the pass below is the marker's doing and not an accidentally clean tree.
            pinned = pathlib.Path(t) / "pinned"
            _mirror_target(root, pinned)
            (pinned / "SKILL.md").write_text("# deliberately old\n", encoding="utf-8")
            unpinned = _run(root, "--check", "--target", str(pinned))
            self.assertNotEqual(unpinned.returncode, 0, unpinned.stdout)
            self.assertEqual(_check_count(unpinned.stdout), 1)

            (pinned / ".local").mkdir()
            (pinned / ".local" / "forward-port.pin").write_text("held at v4.1.0\n",
                                                               encoding="utf-8")
            r = _run(root, "--check", "--target", str(pinned))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("pinned", r.stdout)
            self.assertEqual((pinned / "SKILL.md").read_text(encoding="utf-8"),
                             "# deliberately old\n")


class AgentsPointerTests(unittest.TestCase):
    def test_agents_md_references_the_script(self) -> None:
        text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("forward-port.sh", text)

    def test_agents_md_documents_the_drift_check(self) -> None:
        text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("forward-port.sh --check", text)
        self.assertIn("forward-port.pin", text)


if __name__ == "__main__":
    unittest.main()
