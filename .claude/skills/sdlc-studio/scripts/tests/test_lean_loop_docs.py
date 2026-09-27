"""US0956: the shipped docs teach the lean loop once, and its numbers come from the code.

`reference-sprint.md#the-loop` is the one enumeration of the sprint loop. Every other doc links
it, and any loop another doc still spells out (a numbered bold list, or an `a -> b -> c` chain)
must name the same steps in the same order, read from the canonical section rather than restated
here. The review round cap and the retro's Try limit are read from `critic.DEFAULT_REVIEW_CEILING`
and `retro.TRY_MAX`, so a change to either constant reddens the doc that states it.

Every test reads THIS repository's shipped skill, as the criteria name it.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

critic = loader.load_script("critic")
retro = loader.load_script("retro")
sprint = loader.load_script("sprint")

# parents: [0] tests [1] scripts [2] the shipped skill.
SKILL = Path(__file__).resolve().parents[2]

#: The loop the code runs, in order. The one hand list here, and the thing AC1 asserts.
LOOP = ("plan and approve", "build", "review", "close", "sign", "learn")

_STEP = re.compile(r"^(\d+)\.\s+\*\*([^*\n]+?)\*\*", re.M)
_SURFACE_ROW = re.compile(r"^\|\s*`([\w.]+\.py(?: [\w-]+)+)`\s*\|\s*$", re.M)
_SPAN = re.compile(r"`([^`\n]+)`")
#: A chain step: letters, spaces and inner hyphens (`commit-green`), ending on a letter.
_CHAIN_STEP = r"[A-Za-z](?:[A-Za-z +-]*[A-Za-z])?"
_CHAIN = re.compile(rf"{_CHAIN_STEP}(?:\s*->\s*{_CHAIN_STEP}){{2,}}")


def _read(rel: str) -> str:
    return (SKILL / rel).read_text(encoding="utf-8")


def _norm(head: str) -> str:
    return " ".join(re.sub(r"[^a-z ]", " ", head.lower()).split())


def section(text: str, heading: str) -> str:
    """The body under `## <heading>`, down to the next `## ` heading."""
    m = re.search(rf"^## {re.escape(heading)}[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        raise AssertionError(f"no '## {heading}' section")
    return m.group(1)


def loop_steps(text: str) -> list[tuple[int, str, str]]:
    """(number, normalised head, body) for each top-level step of `## The loop`."""
    body = section(text, "The loop")
    marks = list(_STEP.finditer(body))
    return [(int(m.group(1)), _norm(m.group(2)),
             body[m.end():marks[i + 1].start() if i + 1 < len(marks) else len(body)])
            for i, m in enumerate(marks)]


def canonical_loop() -> list[str]:
    return [head for _n, head, _b in loop_steps(_read("reference-sprint.md"))]


def surface() -> set[str]:
    """Every `script.py verb` row of the generated command surface."""
    rows = set(_SURFACE_ROW.findall(_read("reference-scripts-surface.md")))
    if not rows:
        raise AssertionError("reference-scripts-surface.md yielded no command rows")
    return rows


def commands_named(body: str, rows: set[str]) -> list[str]:
    """The surface commands a step's code spans name: a span counts when a leading run of its
    words (script and verb, or script, verb and sub-verb) is a surface row."""
    found = []
    for span in _SPAN.findall(body):
        words = span.split()
        found += [" ".join(words[:k]) for k in range(len(words), 1, -1)
                  if " ".join(words[:k]) in rows][:1]
    return found


def enumerations(text: str) -> list[list[str]]:
    """Each loop a page spells out: a run of three or more numbered bold items, or a chain of
    three or more `->` steps (wrapped lines joined), as normalised step names."""
    out, run, last = [], [], 0
    for m in _STEP.finditer(text):
        n, head = int(m.group(1)), _norm(m.group(2))
        if run and n == last + 1:
            run.append(head)
        else:
            if len(run) >= 3:
                out.append(run)
            run = [head]
        last = n
    if len(run) >= 3:
        out.append(run)
    flat = " ".join(text.split())
    out += [[_norm(part) for part in chain.split("->")] for chain in _CHAIN.findall(flat)]
    return out


def stray_loops(text: str, canon: list[str]) -> list[list[str]]:
    return [e for e in enumerations(text) if e != canon]


class LoopDocTests(unittest.TestCase):

    def test_the_loop_lists_its_steps_in_order_and_each_resolves(self) -> None:
        """AC1. MUTANTS: HEAD's nine-step loop (tranche audit, triage STOP, Reject -> repair,
        a full-diff critic at the close); a step renamed or reordered; a step naming no
        command on the surface; a review step with no cap or no carry."""
        steps = loop_steps(_read("reference-sprint.md"))
        self.assertEqual([n for n, _h, _b in steps], list(range(1, len(steps) + 1)),
                         "the loop's steps are not numbered 1..n")
        self.assertEqual([h for _n, h, _b in steps], list(LOOP))
        rows = surface()
        for _n, head, body in steps:
            self.assertTrue(commands_named(body, rows),
                            f"step '{head}' names no command in reference-scripts-surface.md")
        review = dict((h, b) for _n, h, b in steps)["review"]
        for cmd in ("critic.py brief", "critic.py record"):
            self.assertIn(cmd, commands_named(review, rows))
        self.assertRegex(review, r"(?i)\bone\b[^.]*\breviewer\b")
        self.assertRegex(review, r"(?i)\bcap\b")
        self.assertRegex(review, r"(?i)\bcarri(?:ed|es)\b")
        body = section(_read("reference-sprint.md"), "The loop")
        for retired in (r"(?i)tranche audit", r"(?i)triage stop", r"(?i)reject\s*->\s*repair",
                        r"(?i)full-diff"):
            self.assertNotRegex(body, retired)
        # Controls: the resolver accepts a real command and refuses a verb the surface lacks.
        self.assertEqual(commands_named("run `sprint.py lane brief --units X`", rows),
                         ["sprint.py lane brief"])
        self.assertEqual(commands_named("run `sprint.py review-batch` and `gate.py`", rows), [])

    def test_there_is_one_canonical_loop(self) -> None:
        """AC2. MUTANTS: help/sprint.md keeping its eight-step 'What happens' list; an arrow
        chain naming another loop (implement -> test -> gate -> critic -> commit-green); a page
        dropping the link."""
        canon = canonical_loop()
        self.assertEqual(canon, list(LOOP))
        for rel in ("help/sprint.md", "help/getting-started.md"):
            text = _read(rel)
            self.assertIn("reference-sprint.md#the-loop", text, f"{rel} does not link the loop")
            self.assertEqual(stray_loops(text, canon), [],
                             f"{rel} enumerates a loop other than reference-sprint.md#the-loop")
        # Controls: both enumeration shapes are seen, and the canonical chain is allowed.
        self.assertTrue(stray_loops("1. **Plan**\n2. **Tranche audit**\n3. **Build**\n", canon))
        self.assertTrue(stray_loops("the loop (implement -> test ->\ngate -> critic)", canon))
        self.assertFalse(stray_loops(
            "plan and approve -> build -> review -> close -> sign -> learn", canon))
        self.assertFalse(stray_loops("1. **Build the base.**\n2. **Then hand it on.**", canon))

    def test_the_review_cap_matches_the_code(self) -> None:
        """AC3. MUTANTS: HEAD's hand-typed '(`review.max_rounds`, 2)' naming no source; the
        constant changed to 3 with the doc left at 2; a carry passage deleted."""
        cap = critic.DEFAULT_REVIEW_CEILING
        text = _read("reference-review.md")
        paras = [p for p in re.split(r"\n\s*\n", text) if "DEFAULT_REVIEW_CEILING" in p]
        self.assertTrue(paras, "reference-review.md does not name critic.DEFAULT_REVIEW_CEILING")
        para = paras[0]
        self.assertIn("`review.max_rounds`", para, "the override is not named beside the cap")
        stated = re.findall(r"(?i)\bcap (?:is|of) \**(\d+)", para)
        self.assertTrue(stated, "the cap's value is not stated beside its source")
        self.assertEqual({int(n) for n in stated}, {cap})
        self.assertRegex(para, r"(?i)\bcarri(?:es|ed)\b")
        self.assertRegex(para, r"(?i)\bbug\b")
        self.assertRegex(para, r"(?i)\bbatch\b")
        # Every cap value the page states elsewhere agrees with the code, too.
        elsewhere = re.findall(r"(?i)\bcap (?:is|of) \**(\d+)|`review\.max_rounds`,? \**(\d+)",
                               text)
        self.assertEqual({int(a or b) for a, b in elsewhere}, {cap})

    def test_the_signed_outcomes_match_the_code(self) -> None:
        """The loop's account of what `sprint sign` records, read from `SIGNED_OUTCOMES`.
        MUTANT: round 1's '`stopped` from a partial or missed one', which the signature never
        writes; the mapping changed in the code with the doc left behind."""
        text = " ".join(_read("reference-sprint.md").split())
        m = re.search(r"the signature records its outcome[^.]*\.", text)
        self.assertIsNotNone(m, "reference-sprint.md does not say what the signature records")
        said = m.group(0)
        for verdict, outcome in sprint.SIGNED_OUTCOMES.items():
            self.assertRegex(said, rf"`{re.escape(outcome)}` from an? {verdict}\b",
                             f"the {verdict} verdict's outcome is not `{outcome}`")
        named = set(re.findall(r"`([a-z-]+)`", said)) & set(sprint.run_state.OUTCOMES)
        self.assertEqual(named, set(sprint.SIGNED_OUTCOMES.values()),
                         "the passage names an outcome the signature does not record")

    def test_the_retro_help_matches_the_validator(self) -> None:
        """AC4. MUTANTS: HEAD's help, which names only the older sections; a Try limit typed
        as a number `retro.TRY_MAX` does not hold; a shape missing Stop."""
        text = _read("help/retro.md")
        for name in retro.KEEP_STOP_TRY:
            self.assertRegex(text, rf"(?m)^## {name}$", f"help/retro.md shows no '## {name}'")
        limits = re.findall(r"(?i)\bat most (\d+) (?:Try )?items?\b", text)
        self.assertTrue(limits, "help/retro.md states no Try limit")
        self.assertEqual({int(n) for n in limits}, {retro.TRY_MAX})
        # The shape shown is one the validator accepts, placeholders aside.
        block = re.search(r"```markdown\n(.*?)```", text, re.S)
        self.assertIsNotNone(block, "help/retro.md shows no example retro")
        self.assertTrue(retro.is_three_line(block.group(1)))
        self.assertEqual(retro.three_line_errors(block.group(1)), [])


if __name__ == "__main__":
    unittest.main()
