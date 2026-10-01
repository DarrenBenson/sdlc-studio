"""BG0834: `persona generate --team` records a default as a default, never as an answer.

Step 2 let a headless run "take the defaults", and nothing said how a default is reported: a
worker's report said three questions were answered and the team accepted when no question was
put. Step 1's discoveries table gains a third mark, `defaulted`, and Step 2 tells a headless run
to put it on every item it did not ask and never to report a default as answered or accepted.
"""
from __future__ import annotations

# test-census-subject: .claude/skills/sdlc-studio/reference-persona-generate.md
import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent.parent
DOC = SKILL / "reference-persona-generate.md"


def _step(text: str, heading: str) -> str:
    start = text.index(heading)
    nxt = re.search(r"^#{2,3} ", text[start + len(heading):], re.M)
    return text[start:start + len(heading) + nxt.start()] if nxt else text[start:]


class PersonaGenerateAnswersTests(unittest.TestCase):
    def test_defaults_are_recorded_as_defaults(self) -> None:
        """AC1. MUTANT: HEAD, whose table admits only `inferred` and `unknown` and whose headless
        line says only 'take the defaults'. MUTANT: add the mark to Step 1 but leave Step 2's
        headless line as it was - the run is never told to use it, or not to call it an answer.
        MUTANT: forbid only one of the two - 'never' must govern the clause naming each word."""
        text = DOC.read_text(encoding="utf-8")
        team = text[text.index("## `--team` {#team}"):]
        step1 = _step(team, "### Step 1: Analyse")
        step2 = _step(team, "### Step 2: Ask when unsure")
        for mark in ("`inferred`", "`unknown`", "`defaulted`"):
            self.assertIn(mark, step1, f"the discoveries table does not admit {mark}")
        headless = " ".join(" ".join(para.split()) for para in step2.split("\n\n")
                            if "Headless" in para)
        self.assertIn("`defaulted`", headless, "Step 2's headless paragraph does not say to mark "
                                               "an unasked item `defaulted`")
        for word in ("answered", "accepted"):
            self.assertRegex(headless, rf"\bnever\b[^.,;:]*\b{word}\b",
                             f"Step 2 does not forbid reporting a default as {word}")


if __name__ == "__main__":
    unittest.main()
