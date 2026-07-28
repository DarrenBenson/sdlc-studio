"""The pre-commit hook must not understate what the artefact gate costs (BG0351).

The hook described the gate to its reader as "fast, ~1s". Measured cold in fresh
processes on this repo the same gate was 32.9s - wrong by a factor of thirty-three, and
the largest single lane in the hook was the one an operator had been told to ignore. A
wrong cost claim is not a cosmetic defect: it is what decides whether anybody goes
looking when a commit starts taking half a minute.

Nothing executes a comment, so nothing but a test stops "fast, ~1s" being written back.
The assertion is deliberately an order-of-magnitude floor rather than today's number:
pinning the exact figure would make every genuine speed-up a test failure, which is how
a guard gets deleted.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".githooks" / "pre-commit"

#: Seconds below which a claim about the WHOLE artefact gate is not credible. The gate
#: runs a conformance sweep, a reconcile sweep, a validate sweep and a dozen more lanes
#: over the artefact graph; it has never been a one-second check on any tree with work in
#: it, and the measurement that produced this bug was 32.9s.
MIN_CREDIBLE_SECONDS = 5.0


def _gate_comment_block() -> str:
    """The comment paragraph immediately preceding the gate.py invocation in the hook."""
    lines = HOOK.read_text(encoding="utf-8").splitlines()
    idx = next(i for i, ln in enumerate(lines) if 'gate.py" --root .' in ln and "if " in ln)
    block: list[str] = []
    for ln in reversed(lines[:idx]):
        if not ln.startswith("#"):
            break
        block.append(ln)
    return "\n".join(reversed(block))


class GateCostClaimTests(unittest.TestCase):
    def test_the_hook_does_not_call_the_artefact_gate_fast(self) -> None:
        block = _gate_comment_block()
        self.assertNotIn("fast, ~1s", block,
                         "the artefact gate was 32.9s when this claim said ~1s")
        self.assertNotRegex(
            block, r"\(fast[,)]",
            "'fast' is a claim about cost; state the measured seconds instead")

    def test_every_second_figure_claimed_for_the_gate_is_credible(self) -> None:
        block = _gate_comment_block()
        claims = [float(x) for x in re.findall(r"~\s*([0-9]+(?:\.[0-9]+)?)\s*s\b", block)]
        # Historical figures are quoted in this block on purpose (the 32.9s that produced
        # the bug), so the floor is applied to the SMALLEST claim: an understated one is
        # the failure mode, an overstated one is not.
        self.assertTrue(claims, "the block must state what the gate costs, in seconds")
        self.assertGreaterEqual(
            min(claims), MIN_CREDIBLE_SECONDS,
            f"a ~{min(claims):g}s claim for the whole artefact gate is not credible; "
            f"the measured cost has never been under {MIN_CREDIBLE_SECONDS:g}s")

    def test_the_reader_is_pointed_at_the_live_number(self) -> None:
        """A number in a comment rots. The gate prints its own cost every run, so the
        comment has to say where today's figure comes from."""
        self.assertIn("gate cost:", _gate_comment_block())


if __name__ == "__main__":
    unittest.main()
