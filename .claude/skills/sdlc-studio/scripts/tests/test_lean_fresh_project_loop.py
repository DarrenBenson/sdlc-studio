"""US0950: a fresh project briefs and records its one review on the shipped defaults.

`critic.py brief` resolves its seat through the resolver `persona_resolve.py resolve` uses: the
project's role-matched card, else the shipped one (it does not judge the review sections). A fresh `init run` project seeds no seat
card, so before this the brief refused and the lean loop dead-ended at its one review.

Every test drives the shipped entry points in a throwaway `init run` project that cleans itself
up; none reads this repository.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

_SCRIPTS = Path(__file__).resolve().parent.parent
_ID = re.compile(r"created (\S+)")
#: The line `critic.py brief` names its charter on.
_CHARTER = re.compile(r"Read and adopt the charter at\s+(\S+)")


def _cli(root: Path, script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(_SCRIPTS / script), *args, "--root", str(root)],
        cwd=root, env=gitutil.git_env(), capture_output=True, text=True, timeout=300)


def _ok(root: Path, script: str, *args: str) -> str:
    proc = _cli(root, script, *args)
    if proc.returncode != 0:
        raise AssertionError(f"{script} {' '.join(args)} exited {proc.returncode}:\n"
                             f"{proc.stdout}\n{proc.stderr}")
    return proc.stdout


def _commit(root: Path, message: str) -> None:
    for argv in (["add", "-A"], ["commit", "-q", "--allow-empty", "-m", message]):
        subprocess.run(["git", "-C", str(root), *argv], env=gitutil.git_env(), check=True,
                       capture_output=True)


def _fresh(root: Path) -> str:
    """A fresh `init run` project on the shipped config with one story whose `Verify:` line
    goes green once `src/widget.py` exists. Returns the story id."""
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], env=gitutil.git_env(),
                   check=True, capture_output=True)
    _ok(root, "init.py", "run")
    _commit(root, "init")
    epic = _ID.search(_ok(root, "artifact.py", "new", "--type", "epic",
                          "--title", "Widgets")).group(1)
    story = _ID.search(_ok(root, "artifact.py", "new", "--type", "story", "--title", "A widget",
                           "--epic", epic, "--points", "1", "--affects", "src/widget.py",
                           "--ac", "the widget exists",
                           "--verify", "shell test -f src/widget.py")).group(1)
    _commit(root, "story")
    return story


def _charter(brief: str) -> Path:
    m = _CHARTER.search(brief)
    if m is None:
        raise AssertionError(f"the brief names no charter:\n{brief[:400]}")
    return Path(m.group(1))


def _resolved(root: Path, seat: str) -> str:
    """What `persona_resolve.py resolve --seat <seat> --render review` prints for `root`."""
    return _ok(root, "persona_resolve.py", "resolve", "--seat", seat, "--render", "review")


class FreshLoopTests(unittest.TestCase):
    def test_brief_falls_back_to_the_shipped_seat(self) -> None:
        """AC1. MUTANTS: HEAD's lookup (`personas/seats/<seat>.md` or refuse) exits 1 naming
        `available seats: none`; a fallback to the generic amigo schema names a charter that
        `resolve` does not print."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            story = _fresh(root)
            self.assertFalse((root / "sdlc-studio" / "personas" / "seats").exists(),
                             "the fixture is not fresh: init seeded seat cards")
            r = _cli(root, "critic.py", "brief", "--unit", story, "--seat", "qa")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertIn("You are the qa review seat", r.stdout)
            charter = _charter(r.stdout)
            printed = _resolved(root, "qa")
            self.assertTrue(charter.is_file(), f"the brief's charter {charter} does not exist")
            self.assertTrue(printed.rstrip().endswith(
                charter.read_text(encoding="utf-8").rstrip()),
                f"the brief's charter {charter} is not the one `resolve` prints")
            self.assertIn("## Lens", printed, "resolve printed no review render")

    def test_a_project_seat_card_wins(self) -> None:
        """AC2. MUTANTS: a fallback that always reads the shipped card names the shipped
        charter here, not the project's; a second resolver that keeps HEAD's filename lookup in
        front of the shipped fallback misses a generated card named after its person, which
        `persona_resolve` matches on its declared role."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            story = _fresh(root)
            seats = root / "sdlc-studio" / "personas" / "seats"
            seats.mkdir(parents=True)
            for name in ("qa.md", "priya.md"):
                with self.subTest(card=name):
                    for old in seats.glob("*.md"):
                        old.unlink()
                    card = seats / name
                    card.write_text("<!-- role: qa -->\n# Priya Raman - QA amigo\n\n"
                                    "## Lens\n\nThe project's own QA lens.\n\n"
                                    "## Pushes Back When\n\nA criterion cannot fail.\n\n"
                                    "## Shadow\n\nOver-testing.\n", encoding="utf-8")
                    r = _cli(root, "critic.py", "brief", "--unit", story, "--seat", "qa")
                    self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                    self.assertEqual(card.resolve(), _charter(r.stdout).resolve(),
                                     "the brief did not carry the project's own card")
                    self.assertIn("The project's own QA lens.", _resolved(root, "qa"))

    def test_the_lean_loop_runs_on_shipped_defaults(self) -> None:
        """AC3. MUTANTS: HEAD's seat lookup (the brief refuses on the fresh project); a record
        that refuses an unbriefed verdict (US0923 retired it; the loop dead-ends at review)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            story = _fresh(root)
            _ok(root, "transition.py", "set", story, "Ready")
            _commit(root, "ready")
            _ok(root, "sprint.py", "plan", "--stories", "Ready", "--sprint-goal",
                "A widget ships", "--write", "--no-fetch")
            _commit(root, "plan")
            (root / "src").mkdir()
            (root / "src" / "widget.py").write_text("x = 1\n", encoding="utf-8")
            _commit(root, "widget")
            _ok(root, "verify_ac.py", "run", "--id", story)
            brief = _ok(root, "critic.py", "brief", "--unit", story, "--seat", "qa")
            self.assertIn("You are the qa review seat", brief)
            _ok(root, "critic.py", "record", "--unit", story, "--verdict", "APPROVE",
                "--reviewer", "qa seat", "--author", "engineering seat")
            _ok(root, "transition.py", "set", story, "Review")
            _commit(root, "delivered")
            # A bare close scaffolds the retro, records the goal verdict and stops (exit 1 by
            # design, refusing nothing); the operator fills the retro's three slots and the
            # close that names it files the report.
            scaffold = _cli(root, "sprint.py", "close", "--goal-verdict", "achieved",
                            "--note", "it shipped")
            self.assertIn("scaffolded", scaffold.stdout, scaffold.stdout + scaffold.stderr)
            self.assertNotIn("refused", scaffold.stdout + scaffold.stderr)
            retro = next((root / "sdlc-studio" / "retros").glob("RETRO*-*.md"))
            text = retro.read_text(encoding="utf-8")
            for slot, words in (("keep", "small batches"), ("stop", "nothing"),
                                ("try", "more")):
                text = text.replace("{{" + slot + "}}", words)
            retro.write_text(text, encoding="utf-8")
            _commit(root, "retro")
            _ok(root, "sprint.py", "close", "--retro", retro.name.split("-", 1)[0])
            _commit(root, "closed")
            _ok(root, "sprint.py", "sign", "--principal", "the operator")
            art = next((root / "sdlc-studio" / "stories").glob(f"{story}-*.md"))
            self.assertRegex(art.read_text(encoding="utf-8"), r"(?m)^> \*\*Status:\*\* Done\b",
                             "the story did not end Done")


if __name__ == "__main__":
    unittest.main()
