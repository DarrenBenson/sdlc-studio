"""BG0814: the create path's two reviews read as steps the agent performs.

A fresh agent running `epic` and `story` in an empty repository skipped the Three Amigos step
("no persona files exist yet") and the story cohesion review (labelled Automatic, after the
Report). These tests read THIS repository's shipped workflow docs, as the criteria name them,
and resolve the seats the docs name through the shipped resolver in a throwaway git repository.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

# parents: [0] tests [1] scripts [2] the shipped skill.
SKILL = Path(__file__).resolve().parents[2]
RESOLVER = SKILL / "scripts" / "persona_resolve.py"
AMIGO_DOCS = ("reference-epic.md", "reference-story.md", "help/epic.md", "help/story.md")
# The per-seat focus lists every Three Amigos step points to.
FOCUS_DOC = "reference-workflow-personas.md"
# Amigo names the shipped seats no longer carry; the resolver prints the live ones.
RETIRED_AMIGOS = ("Sarah Chen", "Marcus Johnson", "Priya Sharma")
# The command a Three Amigos step shows: the seat alternation and the render it names.
SEAT_COMMAND = re.compile(r"persona_resolve\.py resolve --seat <([a-z|]+)> --render (\w+)")
# A top-level numbered item ("7. ", "3b. ") or a heading or rule ends a step's block.
STEP_START = re.compile(r"^(\d+[a-z]?)\. ")
BLOCK_END = re.compile(r"^(\d+[a-z]?\. |#|---)")


def _read(rel: str) -> str:
    return (SKILL / rel).read_text(encoding="utf-8")


def _steps(text: str) -> list[tuple[str, str]]:
    """Every top-level numbered item as (first line, whole block), in document order."""
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines):
        if not STEP_START.match(line):
            continue
        end = i + 1
        while end < len(lines) and not BLOCK_END.match(lines[end]):
            end += 1
        out.append((line, "\n".join(lines[i:end])))
    return out


def _amigo_steps(rel: str) -> list[str]:
    return [block for head, block in _steps(_read(rel)) if "Three Amigos" in head]


def _story_workflow() -> str:
    """The `## /sdlc-studio story - Step by Step` section of reference-story.md."""
    text = _read("reference-story.md")
    start = text.index("## /sdlc-studio story - Step by Step")
    end = text.index("\n## ", start + 1)
    return text[start:end]


class CreatePathReviewTests(unittest.TestCase):

    def test_the_amigo_step_names_the_shipped_seats(self) -> None:
        """AC1. MUTANTS: the rc.1 wording (focus lists only); a step naming the command but not
        that the seats ship with the skill; a help file with no Three Amigos step at all; the
        focus-list doc still naming Sarah Chen, or not naming the resolver."""
        for rel in AMIGO_DOCS:
            steps = _amigo_steps(rel)
            self.assertTrue(steps, f"{rel} has no Three Amigos step")
            for block in steps:
                self.assertRegex(block, SEAT_COMMAND, f"{rel}: a Three Amigos step names no "
                                 "persona_resolve.py resolve --seat ... --render review command")
                self.assertEqual(SEAT_COMMAND.search(block).group(2), "review", rel)
                flat = " ".join(block.split())
                self.assertRegex(flat, r"(?i)seats ship with the skill",
                                 f"{rel}: a Three Amigos step never says the seats ship with "
                                 "the skill")
                self.assertRegex(flat, r"(?i)no project (user )?persona",
                                 f"{rel}: a Three Amigos step leaves project personas as a "
                                 "precondition")
        # The focus-list doc the steps point to names the resolver and no retired amigo.
        focus = _read(FOCUS_DOC)
        match = SEAT_COMMAND.search(focus)
        self.assertIsNotNone(match, f"{FOCUS_DOC} never names the resolver command")
        self.assertEqual(match.group(2), "review", FOCUS_DOC)
        self.assertRegex(" ".join(focus.replace(">", " ").split()),
                         r"(?i)seats ship with the skill", FOCUS_DOC)
        for name in RETIRED_AMIGOS:
            self.assertNotIn(name, focus, f"{FOCUS_DOC} still names the retired amigo {name}")

    def test_the_named_seats_resolve_in_an_empty_project(self) -> None:
        """AC2. MUTANTS: a step naming 'po' (the resolver refuses it); a step naming
        '--render work' (argparse refuses it); a resolver that needs an sdlc-studio/ tree."""
        commands = set()
        for rel in AMIGO_DOCS:
            for block in _amigo_steps(rel):
                match = SEAT_COMMAND.search(block)
                self.assertIsNotNone(match, rel)
                commands.update((seat, match.group(2)) for seat in match.group(1).split("|"))
        match = SEAT_COMMAND.search(_read(FOCUS_DOC))
        self.assertIsNotNone(match, FOCUS_DOC)
        commands.update((seat, match.group(2)) for seat in match.group(1).split("|"))
        self.assertEqual({seat for seat, _ in commands}, {"product", "engineering", "qa"},
                         "the steps do not name the three amigo seats")
        with tempfile.TemporaryDirectory() as tmp:
            gitutil.git(["init", "-q"], cwd=tmp)
            self.assertFalse((Path(tmp) / "sdlc-studio").exists())
            for seat, render in sorted(commands):
                proc = subprocess.run(
                    [sys.executable, str(RESOLVER), "resolve", "--seat", seat, "--render", render],
                    cwd=tmp, env=gitutil.git_env(), capture_output=True, text=True, timeout=60)
                self.assertEqual(proc.returncode, 0, f"{seat}/{render}: {proc.stderr}")
                self.assertIn(f"<!-- role: {seat} -->", proc.stdout, f"{seat}: no charter")
                self.assertIn("## Lens", proc.stdout, f"{seat}: not the review render")

    def test_the_cohesion_review_runs_before_the_report(self) -> None:
        """AC3. MUTANTS: the rc.1 order (Report, then an Automatic cohesion step); the steps
        swapped back; a Report step that does not carry the cohesion findings."""
        steps = _steps(_story_workflow())
        heads = [head for head, _ in steps]
        cohesion = [i for i, head in enumerate(heads) if re.search(r"(?i)cohesion", head)]
        report = [i for i, head in enumerate(heads) if re.search(r"\*\*Report\*\*", head)]
        self.assertEqual(len(cohesion), 1, heads)
        self.assertEqual(len(report), 1, heads)
        self.assertLess(cohesion[0], report[0], "the cohesion review comes after the Report")
        self.assertNotRegex(steps[cohesion[0]][1], r"(?i)automatic",
                            "the cohesion step is labelled Automatic")
        self.assertRegex(steps[report[0]][1], r"(?i)cohesion",
                         "the Report step does not list the cohesion findings")
        # Each step carries its own number: no list restarting at 1 hides the order.
        numbers = [STEP_START.match(head).group(1) for head in heads]
        self.assertEqual(len(numbers), len(set(numbers)), f"a step number repeats: {numbers}")

    def test_the_story_help_names_the_cohesion_review_early(self) -> None:
        """AC4. MUTANTS: the rc.1 help (only an '(Automatic)' heading at line 140); a mention
        at line 61; a heading still reading 'Cohesion Review (Automatic)'; an intro naming
        `/sdlc-studio epic` while the quick reference elsewhere supplies the story command."""
        lines = _read("help/story.md").splitlines()
        # One passage (a blank-line-separated block) names both the command and the review.
        passages = "\n".join(lines[:60]).split("\n\n")
        self.assertTrue(
            any(re.search(r"(?i)cohesion review", block) and "`/sdlc-studio story`" in block
                for block in passages),
            "no passage in help/story.md's first 60 lines names the cohesion review as part "
            "of `/sdlc-studio story`")
        headings = [line for line in lines if line.startswith("#")]
        for line in headings:
            if re.search(r"(?i)cohesion", line):
                self.assertNotRegex(line, r"(?i)automatic", line)


if __name__ == "__main__":
    unittest.main()
