"""US1116: the commit-msg hook's paste-ready trailers skip an id a `Mentions:` line accounts for.

When `check-commit-msg --strict` refuses, the hook prints a `Refs:` line to paste for each id the
subject names and no trailer accounts for. It read only `Refs:` lines, so beside a
`Mentions: <id>` line it still asked for `Refs: <id>`: the false attribution `Mentions:` exists
to avoid. Each test runs the real hook, the way git invokes it, in a throwaway repository.
"""
# test-census-subject: .githooks/commit-msg
from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".githooks" / "commit-msg"
SUBJECT = "feat(US1110): repair the lane BG0989 raised, beside BG1000"


def _load_gitutil():
    """The shipped git-fixture helper, which confines every fixture git call to the fixture.
    Loaded rather than re-implemented, so this module carries no second copy of its list."""
    path = REPO / ".claude/skills/sdlc-studio/scripts/tests/gitutil.py"
    spec = importlib.util.spec_from_file_location("_commit_msg_mentions_gitutil", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


gitutil = _load_gitutil()


def _env() -> dict:
    return gitutil.git_env()


def _hook(message: str) -> subprocess.CompletedProcess:
    """The commit-msg hook on `message`, run in a fixture repository whose skill scripts are
    this tree's own, so the refusal the script makes is the one under test."""
    with tempfile.TemporaryDirectory() as d:
        repo = Path(d)
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=_env())
        skill = repo / ".claude" / "skills" / "sdlc-studio"
        skill.mkdir(parents=True)
        (skill / "scripts").symlink_to(REPO / ".claude" / "skills" / "sdlc-studio" / "scripts")
        msg = repo / "COMMIT_EDITMSG"
        msg.write_text(message, encoding="utf-8")
        return subprocess.run(["bash", str(HOOK), str(msg)], cwd=repo, capture_output=True,
                              text=True, env=_env(), timeout=120)


def _pasted(out: str) -> list[str]:
    """The trailer lines the hook offers to paste: each output line that is only a trailer."""
    return re.findall(r"^\s*((?:Refs|Mentions): \S+)\s*$", out, re.MULTILINE)


class CommitMsgMentionsTests(unittest.TestCase):

    def test_the_hint_skips_an_id_a_mentions_line_covers(self):
        # AC1. Must fail on: `covered` grepping only `^Refs:` (a `Refs: BG0989` line is then
        # printed), or the hint offering no `Mentions:` line.
        for trailer in ("Mentions: BG0989", "mentions: BG0989"):
            with self.subTest(trailer=trailer):
                r = _hook(f"{SUBJECT}\n\n{trailer}\n")
                out = r.stdout + r.stderr
                self.assertNotEqual(r.returncode, 0, out)
                self.assertEqual(_pasted(out),
                                 ["Refs: BG1000", "Refs: US1110", "Mentions: <id>"], out)
                self.assertNotIn("Refs: BG0989", out)
                self.assertIn("only mentions", out)
        # Positive control: with the two owed `Refs:` lines added, the same message passes.
        r = _hook(f"{SUBJECT}\n\nRefs: US1110\nRefs: BG1000\nMentions: BG0989\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((r.stdout + r.stderr).strip(), "ok   message-refs")

    def test_the_lane_rule_names_mentions(self):
        # AC2. Must fail on: the `run "message-refs"` rule string left naming only `Refs:`.
        r = subprocess.run(["bash", str(HOOK), "--list"], cwd=REPO, capture_output=True,
                           text=True, env=_env(), timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        rules = dict(ln.split("\t", 1) for ln in r.stdout.splitlines() if "\t" in ln)
        rule = rules["message-refs"]
        self.assertIn("Refs: <id> for an id that owns the commit's files", rule)
        self.assertIn("Mentions: <id> for an id that owns none of them", rule)

    def test_enable_hooks_names_mentions(self):
        # The line `enable-hooks.sh` prints about the rule names both trailers.
        with tempfile.TemporaryDirectory() as d:
            clone = Path(d)
            subprocess.run(["git", "init", "-q"], cwd=clone, check=True, env=_env())
            (clone / ".githooks").mkdir()
            shutil.copy(HOOK, clone / ".githooks" / "commit-msg")
            (clone / "tools").mkdir()
            shutil.copy(REPO / "tools" / "enable-hooks.sh", clone / "tools" / "enable-hooks.sh")
            r = subprocess.run(["bash", "tools/enable-hooks.sh"], cwd=clone, capture_output=True,
                               text=True, env=_env(), timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        line = next(ln for ln in r.stdout.splitlines() if ln.startswith("A multi-id commit"))
        self.assertIn("'Refs: <id>' trailer per owning id", line)
        self.assertIn("'Mentions: <id>'", line)


class DerivedMentionsTests(unittest.TestCase):
    """US1133 AC2: an id the subject names but whose `Affects` declares none of the staged files
    gets a `Mentions:` line written for it, never `Refs:`."""

    def test_a_non_owning_id_gets_mentions(self):
        # Must fail on: writing `Refs:` for every id the subject names.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=_env())
            skill = repo / ".claude" / "skills" / "sdlc-studio"
            skill.mkdir(parents=True)
            (skill / "scripts").symlink_to(REPO / ".claude/skills/sdlc-studio/scripts")
            # US1110 owns the staged file; BG0989 is a unit whose Affects names another file;
            # BG1000 has no artefact here at all, so nothing can make it an owner.
            for rel, rid, owned in (("stories", "US1110", "src/lane.py"),
                                    ("bugs", "BG0989", "src/elsewhere.py")):
                folder = repo / "sdlc-studio" / rel
                folder.mkdir(parents=True)
                (folder / f"{rid}-sample.md").write_text(
                    f"# {rid}: sample\n\n> **Status:** In Progress\n> **Affects:** {owned}\n",
                    encoding="utf-8")
            # Committed first, so the one staged change is the source file, not an artefact
            # whose own filename would make its unit an owner.
            subprocess.run(["git", "add", "-A"], cwd=repo, check=True, env=_env())
            subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=repo, check=True,
                           env=_env())
            (repo / "src").mkdir()
            (repo / "src" / "lane.py").write_text("x = 1\n", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=repo, check=True, env=_env())
            msg = repo / "COMMIT_EDITMSG"
            msg.write_text(f"{SUBJECT}\n", encoding="utf-8")
            r = subprocess.run(["bash", str(HOOK), str(msg)], cwd=repo, capture_output=True,
                               text=True, env=_env(), timeout=120)
            after = msg.read_text(encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(
            after, f"{SUBJECT}\n\nRefs: US1110\nMentions: BG0989\nMentions: BG1000\n")
        self.assertNotIn("Refs: BG0989", after)
        self.assertNotIn("Refs: BG1000", after)


if __name__ == "__main__":
    unittest.main()
