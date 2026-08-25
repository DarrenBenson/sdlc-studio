"""BG0606: the six test-plan rows an independent review rejected stay re-bound.

A plan row whose declared mutant cannot fail the test its own criterion names is decoration,
and `plan_execution` reports the criterion covered anyway - it joins on `(criterion, row)` and
never asks which node did the killing. An independent test-plan review found SIX such rows
across US0671, US0674 and US0676 by reading the mutation ledger against the `Verify:` lines by
hand, over three rejection rounds.

The rows were re-bound. This pins that they stay so, and it pins the property rather than the
wording: `testplan derive` reports UNCHANGED only when every criterion has exactly one row and
every row states its own criterion. The three defects the review found - a decoration row, a
row filed under the wrong criterion, and a row FUSED into a neighbour's Title cell where the
parser cannot see it - each move the unit off that shape, so each fails here.

Repo-only: this is a fact about this repository's own artefacts, not shipped behaviour.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO / "tools") not in sys.path:
    sys.path.insert(0, str(REPO / "tools"))
import batch_plan_shape  # noqa: E402 - the module under test, resolved from tools/
#: The three units whose plans the review rejected, and BG0606 itself.
UNITS = ("US0671", "US0674", "US0676")


def _derive(unit: str):
    """`batch_plan_shape.derive_report`, shaped like the CompletedProcess this once used."""
    ok, detail = batch_plan_shape.derive_report(unit)
    return type("R", (), {"returncode": 0 if ok else 1, "stdout": detail, "stderr": ""})()


class BatchPlanShapeTests(unittest.TestCase):
    def _assert_derived_shape(self, unit: str) -> None:
        res = _derive(unit)
        self.assertEqual(0, res.returncode,
                         f"{unit}: derive refused its own plan:\n{res.stdout}{res.stderr}")
        self.assertIn("unchanged", res.stdout,
                      f"{unit}: the plan is no longer the shape `testplan derive` produces, so a "
                      f"row has been added, moved or fused:\n{res.stdout}")

    def test_no_criterion_carries_a_row_its_own_verifier_cannot_reach(self) -> None:
        """MUTANT: restore US0671 AC4's second row - the decoration whose mutant skipped the
        revert loop and left the criterion's own fixture green either way.

        A second row on a criterion is how a decoration row hides: `plan_execution` joins on
        `(criterion, row)`, so the covered verdict comes from the row that DID kill and the one
        that could not is never asked about. Off the derived shape, and caught here."""
        for unit in UNITS:
            with self.subTest(unit=unit):
                self._assert_derived_shape(unit)

    def _titles_match_criteria(self, unit: str) -> None:
        """Every plan row's Title cell states the criterion the row is filed under."""
        import re as _re
        path = next((REPO / "sdlc-studio" / sub).glob(f"{unit}-*.md")
                    for sub in ("stories", "bugs")
                    if list((REPO / "sdlc-studio" / sub).glob(f"{unit}-*.md")))
        text = next(path).read_text(encoding="utf-8")
        criteria = dict(_re.findall(r"^- \[[ x]\] \*\*(AC\d+)\*\* (.+)$", text, _re.M))
        for line in text.splitlines():
            if not line.startswith("| AC"):
                continue
            cells = [c.strip() for c in line.split("|")]
            ac, title = cells[1], cells[3]
            self.assertTrue(criteria.get(ac, "").startswith(title[:40]),
                            f"{unit} {ac}: its row's Title states another criterion - "
                            f"{title[:60]!r} against {criteria.get(ac, '')[:60]!r}")

    def test_no_row_states_a_criterion_other_than_its_own(self) -> None:
        """MUTANT: in US0676, delete AC6 and re-file its row under AC4.

        The review found the stripped-seal row - a REFUSAL claim - sitting on AC4, which is the
        PASS control. A row filed under a criterion that does not claim it reads as evidence for
        something nobody asserted, and `derive` will not reproduce that arrangement."""
        self._assert_derived_shape("US0676")
        # ASSERTED DIRECTLY, not only through `derive`. Reading the Title cells against the
        # criteria is a different question from whether the table is the derived shape, and an
        # independent review found this criterion's verifier a strict SUBSET of its sibling's -
        # it could not fail unless the sibling did.
        self._titles_match_criteria("US0676")

    def test_the_check_can_fail(self) -> None:
        """The paired control. A unit whose plan is NOT in derived shape must be reported, or the
        assertion above would pass on any input and pin nothing.

        BG0463 is the standing example: its criteria are bare `- [ ]` items with no `**ACn**`
        ids, so `derive` yields zero rows for four criteria and refuses.
        """
        res = _derive("BG0463")
        self.assertNotEqual(0, res.returncode,
                            "a unit that cannot derive a plan came back clean, so the check "
                            f"above discriminates nothing:\n{res.stdout}{res.stderr}")


if __name__ == "__main__":
    unittest.main()
