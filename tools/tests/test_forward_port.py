"""tools/forward-port.sh - the dev-repo rsync to the installed copy, guarded (RED first).

The forward-port was hand-typed four times in one day; a wrong --delete without the
.local exclude destroys the installed copy's local state, and BG0100 records what a
wrong direction does. The script wraps the canonical rsync: dry-run by default,
--yes to apply, wrong direction or a non-dev-repo cwd refused loudly.
"""
from __future__ import annotations

import pathlib
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


class AgentsPointerTests(unittest.TestCase):
    def test_agents_md_references_the_script(self) -> None:
        text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("forward-port.sh", text)


if __name__ == "__main__":
    unittest.main()
