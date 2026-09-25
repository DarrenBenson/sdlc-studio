"""US0929: the PRD describes the lean product and lists the outcomes a Sprint Goal can serve.

The outcomes are read by the planner's own reader (`sprint.prd_outcomes`) and the persona
cards by `sprint.persona_cards`, so this file holds no second parser of either and names no
persona or End goal by hand: a card that gains, loses or renumbers an End goal moves what an
outcome may cite. Every `<script>.py <subcommand>` the loop sections name is checked against
that script's own `--help`, so a retired subcommand cannot stay described as current.
"""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
PRD = REPO / "sdlc-studio" / "prd.md"
sys.path.insert(0, str(SCRIPTS))

import sprint  # noqa: E402 - the outcome and persona readers US0927 ships

#: One citation inside an outcome: `(Maya Okafor, End goal 4)`; several are `;`-separated.
_CITE_RE = re.compile(r"([A-Z][\w'-]*(?: [A-Z][\w'-]*)+), End goal (\d+)")
#: A command a section names: a code span opening `<script>.py <subcommand>`.
_COMMAND_RE = re.compile(r"`([a-z_]+)\.py ([a-z][a-z0-9-]*)")
#: What the loop sections must say, as the code runs it today (AC2).
_LOOP_MARKERS = {
    "a Sprint Goal of 20 words or fewer": r"20 words or fewer",
    "the goal traces to an outcome": r"\boutcome",
    "one plan approval": r"approves? the plan once|one plan approval",
    "one reviewer per unit": r"one reviewer",
    "at most two review rounds": r"two rounds",
    "carried known issues": r"known issue",
    "persona rulings through decisions.py rule": r"`decisions\.py rule",
    "the one-page sprint report": r"one-page",
    "failure classes in lessons.jsonl": r"lessons\.jsonl",
}
_RETIRED = ("a learning loop that must produce work",
            "lifted into the store the next `sprint plan` prints unasked")


def outcome_problems(root: Path) -> list[str]:
    """Why the PRD's outcomes do not trace to real persona End goals; empty when they do."""
    outcomes = sprint.prd_outcomes(root)
    if not outcomes:
        return ["the PRD has no parseable `## Outcomes` section"]
    goals = {c["name"]: {n for n, _ in c["end_goals"]} for c in sprint.persona_cards(root)}
    problems = []
    for oid, text in outcomes.items():
        cites = _CITE_RE.findall(text)
        if not cites:
            problems.append(f"{oid} cites no persona End goal: {text}")
        for name, number in cites:
            if name not in goals:
                problems.append(f"{oid} cites {name}, who has no card in sdlc-studio/personas/")
            elif number not in goals[name]:
                problems.append(f"{oid} cites {name} End goal {number}; the card has "
                                f"{sorted(goals[name])}")
    return problems


def section(text: str, heading: str) -> str:
    """The body under `heading` (a whole heading line), up to the next heading of its level or
    above; empty when the heading is absent."""
    level = len(heading) - len(heading.lstrip("#"))
    m = re.search(rf"^{re.escape(heading)}\s*$(.*?)(?=^#{{1,{level}}}\s|\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def subcommands(script: str) -> set[str] | None:
    """The subcommands `<script>.py --help` lists, or None when there is no such script."""
    path = SCRIPTS / f"{script}.py"
    if not path.is_file():
        return None
    out = subprocess.run([sys.executable, str(path), "--help"], capture_output=True,
                         text=True, check=False, cwd=REPO).stdout
    names: set[str] = set()
    for group in re.findall(r"\{([^{}]*)\}", out, re.S):
        names.update(n.strip() for n in group.split(",") if n.strip())
    return names


def unknown_commands(text: str) -> list[str]:
    """Each `<script>.py <subcommand>` in `text` that the script's `--help` does not list."""
    bad = []
    for script, sub in dict.fromkeys(_COMMAND_RE.findall(text)):
        known = subcommands(script)
        if known is None or sub not in known:
            bad.append(f"{script}.py {sub}")
    return bad


def loop_sections(text: str) -> str:
    return section(text, "## Mission") + section(text, "### Core Behaviours")


class PrdRefreshTests(unittest.TestCase):

    def test_every_outcome_traces_to_a_real_end_goal(self):
        """AC1. Mutants: drop the Outcomes section; cite End goal 9 on a real card; cite a
        persona with no card - each must be refused."""
        self.assertEqual([], outcome_problems(REPO))
        self.assertTrue(sprint.prd_outcomes(REPO), "the PRD lists no outcomes")
        prd = PRD.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(REPO / "sdlc-studio" / "personas", root / "sdlc-studio" / "personas")

            def problems_with(prd_text: str) -> list[str]:
                (root / "sdlc-studio" / "prd.md").write_text(prd_text, encoding="utf-8")
                return outcome_problems(root)

            self.assertEqual([], problems_with(prd), "the copied fixture must start clean")
            no_section = re.sub(r"^## Outcomes\s*$", "## Aims", prd, count=1, flags=re.M)
            self.assertNotEqual(prd, no_section)
            self.assertTrue(problems_with(no_section))
            first = next(iter(sprint.prd_outcomes(REPO).values()))
            m = _CITE_RE.search(first)
            bad_goal = prd.replace(m.group(0), f"{m.group(1)}, End goal 9", 1)
            self.assertIn("End goal 9", problems_with(bad_goal)[0])
            no_card = prd.replace(m.group(0), "Ada Lovelace, End goal 1", 1)
            self.assertIn("no card", problems_with(no_card)[0])
            uncited = prd.replace(f"({m.group(0)})", "", 1)
            self.assertNotEqual(prd, uncited)
            self.assertIn("cites no persona", problems_with(uncited)[0])

    def test_the_loop_section_names_only_commands_that_exist(self):
        """AC2. Mutants: name a subcommand the script lacks, or a script that does not exist;
        drop any one loop element from the Mission and Core Behaviours."""
        loop = loop_sections(PRD.read_text(encoding="utf-8"))
        self.assertTrue(loop.strip(), "no Mission or Core Behaviours section found")
        missing = [what for what, pattern in _LOOP_MARKERS.items()
                   if not re.search(pattern, loop, re.I)]
        self.assertEqual([], missing, "the loop sections do not describe these")
        named = _COMMAND_RE.findall(loop)
        self.assertIn(("decisions", "rule"), named)
        self.assertEqual([], unknown_commands(loop))
        # the check itself must be able to refuse
        self.assertEqual(["sprint.py frobnicate"], unknown_commands("`sprint.py frobnicate`"))
        self.assertEqual(["nosuch.py plan"], unknown_commands("`nosuch.py plan`"))
        self.assertEqual([], unknown_commands("`sprint.py plan` and `critic.py brief`"))

    def test_the_retired_learning_loop_is_not_described_as_current(self):
        """AC3. Mutant: restore either retired phrase, or a Learning loop row that names no
        failure class."""
        prd = PRD.read_text(encoding="utf-8")
        present = [phrase for phrase in _RETIRED if phrase in prd]
        self.assertEqual([], present, "the PRD still describes the retired learning loop")
        rows = [line for line in prd.splitlines() if line.startswith("| Learning loop |")]
        self.assertEqual(1, len(rows), "the Feature Inventory has no single Learning loop row")
        self.assertRegex(rows[0], r"failure class")


if __name__ == "__main__":
    unittest.main()
