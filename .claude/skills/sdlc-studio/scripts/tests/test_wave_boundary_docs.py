"""US1142: the sprint reference defines a wave boundary and runs the close in its own fresh session.

A builder's hand-back reaches only the session that spawned its agent, so a session can be
replaced only where no lane is in flight. `reference-sprint.md#wave-boundary` names that point,
the two verbs that cross it (`sprint.py handoff` at the boundary, `sprint.py resume` in the fresh
session) and the close's own fresh session; "The handoff and the run object" tells the run-local
resume brief apart from the retired handoff record; and the toolchain runbook carries a row for
each verb. The verbs are read from `sprint.build_parser()` and the brief's path from
`sprint.RESUME_BRIEF_REL`, so a renamed verb or a moved brief reddens the page that names it.

Every test reads THIS repository's shipped skill, as the criteria name it.
"""
from __future__ import annotations

import argparse
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")

# parents: [0] tests [1] scripts [2] the shipped skill.
SKILL = Path(__file__).resolve().parents[2]

_HEADING = re.compile(r"^(#{2,6}) ", re.M)
_SPRINT_VERB = re.compile(r"`sprint\.py ([a-z][\w-]*)")
_STEP = re.compile(r"^\d+\.\s+\*\*[^*\n]+\*\*", re.M)


def _read(rel: str) -> str:
    return (SKILL / rel).read_text(encoding="utf-8")


def _flat(text: str) -> str:
    return " ".join(text.split())


def raw_section(text: str, pattern: str) -> str:
    """The body under the first heading whose text matches `pattern`, down to the next heading
    of the same or a higher level. Raises when no heading matches."""
    m = re.search(rf"^(#{{2,6}}) [^\n]*{pattern}[^\n]*\n", text, re.M)
    if not m:
        raise AssertionError(f"no heading matching {pattern!r}")
    level, body = len(m.group(1)), text[m.end():]
    for h in _HEADING.finditer(body):
        if len(h.group(1)) <= level:
            return body[:h.start()]
    return body


def section(text: str, pattern: str) -> str:
    """`raw_section`, whitespace-flattened so a sentence wrapped across lines reads as one."""
    return _flat(raw_section(text, pattern))


def sentences(text: str) -> list[str]:
    """`text` split at a full stop or colon followed by a space, so a test can ask that two words
    share one statement rather than merely one section."""
    return [s for s in re.split(r"(?<=[.:])\s+", text) if s]


def parser_verbs() -> set[str]:
    """The top-level verbs `sprint.py`'s own parser accepts."""
    for action in sprint.build_parser()._actions:
        if isinstance(action, argparse._SubParsersAction):
            return set(action.choices)
    raise AssertionError("sprint.build_parser() has no subcommands")


def runbook_rows(text: str, verb: str) -> list[str]:
    """The runbook's table rows whose command cell opens with `sprint.py <verb>`."""
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.lstrip().startswith("|") and len(cells) >= 3 and re.match(
                rf"`sprint\.py {re.escape(verb)}\b", cells[1]):
            rows.append(line)
    return rows


class WaveBoundaryDocTests(unittest.TestCase):
    def test_the_reference_defines_the_boundary_and_names_parser_verbs(self) -> None:
        """AC1. MUTANTS: (1) drop the `{#wave-boundary}` anchor - no section is found; (2) drop
        "accepted" or "none is in flight" from the definition - the definition sentence no longer
        holds both conditions; (3) drop the hand-back sentence; (4) name `sprint.py hand-off` or
        any verb the parser lacks - it is not among `build_parser()`'s choices; (5) move
        `sprint.py resume` out of the fresh-session sentence."""
        body = section(_read("reference-sprint.md"), r"\{#wave-boundary\}")
        said = sentences(body)
        self.assertTrue(any(re.search(r"(?i)\bwave boundary\b", s)
                            and re.search(r"(?i)\bevery lane of the wave\b[^.]*\baccepted\b", s)
                            and re.search(r"(?i)\bnone (?:is )?in flight\b", s) for s in said),
                        "no sentence defines the boundary as every lane accepted and none in "
                        "flight:\n" + body)
        self.assertRegex(body, r"(?i)hand-back reaches only the session that spawned its agent")
        self.assertRegex(body, r"(?i)\bno (?:wave )?boundary falls with a lane in flight\b")
        named = set(_SPRINT_VERB.findall(body))
        self.assertTrue({"handoff", "resume"} <= named, f"the section names {sorted(named)}")
        owned = parser_verbs()
        self.assertEqual(set(), named - owned, "the section names a verb the parser does not own")
        self.assertTrue(any("`sprint.py handoff" in s and re.search(r"(?i)\bboundary\b", s)
                            for s in said), "`sprint.py handoff` is not named at the boundary")
        self.assertTrue(any("`sprint.py resume" in s and re.search(r"(?i)\bfresh session\b", s)
                            for s in said), "`sprint.py resume` is not named in the fresh session")
        # Controls: the parser read is real - it owns the close and lacks a verb it never had;
        # a section ends at the next heading of its own level; and a sentence ends at a full
        # stop or a colon, so "one sentence holds both" is not "the section holds both".
        self.assertIn("close", owned)
        self.assertNotIn("hand-off", owned)
        self.assertEqual("y #### C z", section("## A\nx\n### B {#b}\ny\n#### C\nz\n### D\nw\n",
                                        r"\{#b\}"))
        self.assertEqual(["A b.", "C d:", "e f."], sentences("A b. C d: e f."))

    def test_the_close_runs_in_its_own_fresh_session_and_the_loop_stays_six_steps(self) -> None:
        """AC2. MUTANTS: (1) drop the close's sentence from the section; (2) say the close runs in
        the last wave's session - "own fresh session" is gone; (3) drop "resume brief" from it;
        (4) drop the retro, the report or the sign from the steps it moves; (5) add a seventh
        numbered step to `## The loop`."""
        text = _read("reference-sprint.md")
        body = section(text, r"\{#wave-boundary\}")
        close = [s for s in sentences(body) if re.search(r"(?i)\bown fresh session\b", s)]
        self.assertTrue(close, "the section gives the close no fresh session of its own:\n" + body)
        routed = [s for s in close
                  if all(re.search(rf"(?i)\b{w}\b", s)
                         for w in ("retro", "report", "close", "sign", "resume brief"))]
        self.assertTrue(routed, "no sentence routes the retro, report, close and sign through "
                                "a fresh session started from the resume brief:\n"
                        + "\n".join(close))
        steps = _STEP.findall(raw_section(text, r"The loop$"))
        self.assertEqual(6, len(steps), "the loop under #the-loop is not six steps:\n"
                         + "\n".join(steps))

    def test_the_resume_brief_is_told_apart_from_the_retired_handoff_and_the_runbook_names_both(
            self) -> None:
        """AC3. MUTANTS: (1) restore "No command writes a handoff" with no word on the resume
        brief; (2) drop the brief's run-local path, or name a path other than
        `sprint.RESUME_BRIEF_REL`; (3) drop `sprint.py resume` as its reader; (4) drop the
        sentence saying the signed report replaced the retired handoff record; (5) drop either
        runbook row, or duplicate one."""
        body = section(_read("reference-sprint.md"), r"The handoff and the run object")
        said = sentences(body)
        brief = [s for s in said if re.search(r"(?i)\bresume brief\b", s)]
        self.assertTrue(brief, "the section says nothing of the resume brief:\n" + body)
        joined = " ".join(brief)
        self.assertIn(f"`{sprint.RESUME_BRIEF_REL.as_posix()}`", joined,
                      "the resume brief's run-local path is not the one `sprint.py handoff` "
                      "writes")
        self.assertIn("`sprint.py resume`", joined, "the brief's reader is not named")
        self.assertTrue(any(re.search(r"(?i)\bhandoff record\b", s)
                            and re.search(r"(?i)\bretired\b", s)
                            and re.search(r"(?i)\bsigned report\b", s) for s in said),
                        "no sentence says the signed report replaced the retired handoff "
                        "record:\n" + body)
        self.assertNotRegex(body, r"(?i)\bno command writes a handoff\b")
        runbook = _read("reference-sprint-toolchain.md")
        for verb in ("handoff", "resume"):
            self.assertEqual(1, len(runbook_rows(runbook, verb)),
                             f"the runbook does not carry exactly one `sprint.py {verb}` row")
        # Control: the row reader finds a row the runbook already carried before this unit.
        self.assertEqual(1, len(runbook_rows(runbook, "stop")))


if __name__ == "__main__":
    unittest.main()
