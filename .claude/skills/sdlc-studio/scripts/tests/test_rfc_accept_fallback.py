"""The RFC accept gate's fail-closed fallback names itself in the refusal.

The fallback reads every unsettled decision row anywhere in the file, so an RFC with every
real decision settled can be refused over an EXAMPLE row inside a fenced block. That is a
deliberate trade, not a defect - but an operator meeting the refusal with no signal that it
is the known over-report either edits valid markdown until the tool relents or stops
believing the gate, and the second is worse.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent


def _load():
    spec = importlib.util.spec_from_file_location("transition", DIR / "transition.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["transition"] = mod
    spec.loader.exec_module(mod)
    return mod


#: A well-formed RFC: one Open row in the register, no fence trouble.
CLEAN = (
    "# RFC0001: r\n\n> **Status:** In Review\n\n"
    "## Open Decisions\n\n| # | Decision | Status |\n| --- | --- | --- |\n"
    "| D1 | pick one | Open |\n"
)

#: Every REAL decision settled, and an appendix whose fence is never closed - valid
#: CommonMark (a fence closes at end of document) holding an EXAMPLE row.
FALLBACK = (
    "# RFC0002: r\n\n> **Status:** In Review\n\n"
    "## Open Decisions\n\n| # | Decision | Status |\n| --- | --- | --- |\n"
    "| D1 | pick one | Closed: option A |\n\n"
    "## Appendix\n\n```markdown\n"
    "| # | Decision | Status |\n| --- | --- | --- |\n| D9 | an example row | Open |\n"
)


class FallbackNamedInRefusalTests(unittest.TestCase):

    def test_the_fallback_path_is_reported_by_the_reader(self) -> None:
        mod = _load()
        self.assertEqual(mod._rfc_open_decisions_detail(CLEAN), (["D1"], False))
        rows, used = mod._rfc_open_decisions_detail(FALLBACK)
        self.assertEqual(rows, ["D9"])       # the example row, from outside the register
        self.assertTrue(used)

    def test_the_refusal_says_when_it_came_from_the_fallback(self) -> None:
        mod = _load()
        msg = mod._rfc_accept_gate(FALLBACK, "Accepted")
        self.assertIsNotNone(msg)
        self.assertIn("FAIL-CLOSED fallback", msg)
        self.assertIn("unterminated fence", msg)
        # The trade is stated where the operator meets it, not only in a docstring.
        self.assertIn("false positive", msg)

    def test_an_ordinary_refusal_does_not_claim_the_fallback(self) -> None:
        """The other side of the same signal: a message that says `fallback` on every
        refusal carries no information at all."""
        mod = _load()
        msg = mod._rfc_accept_gate(CLEAN, "Accepted")
        self.assertIsNotNone(msg)
        self.assertIn("D1", msg)
        self.assertNotIn("fallback", msg)

    def test_the_override_escape_is_named_in_both_refusals(self) -> None:
        mod = _load()
        for text in (CLEAN, FALLBACK):
            msg = mod._rfc_accept_gate(text, "Accepted")
            self.assertIn("Decision-Override", msg)
            # `--force` is explicitly NOT the escape; saying so stops the reflex.
            self.assertIn("--force does not bypass", msg)

    def test_a_recorded_override_still_clears_the_fallback_refusal(self) -> None:
        """The escape must work on the path it exists for - if the fallback's false positive
        were unescapable, documenting it would be documenting a dead end."""
        mod = _load()
        text = FALLBACK.replace("> **Status:** In Review\n",
                                "> **Status:** In Review\n> **Decision-Override:** example row\n")
        self.assertIsNone(mod._rfc_accept_gate(text, "Accepted"))

    def test_the_narrow_reader_keeps_its_public_shape(self) -> None:
        """`_rfc_open_decisions` is called by validate.py; it must still return a bare list."""
        mod = _load()
        self.assertEqual(mod._rfc_open_decisions(CLEAN), ["D1"])
        self.assertEqual(mod._rfc_open_decisions(FALLBACK), ["D9"])


if __name__ == "__main__":
    unittest.main()
