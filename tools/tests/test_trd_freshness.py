"""US0059/CR0184: guard the TRD's write-contract and scale claims against drift.

The TRD is a generated blueprint that silently rotted (it described "10 scripts", a
"read-only over the workspace" contract, and a non-existent state file). This guard fails if
any of those specific misleading claims reappear, and checks the script-count claim is in the
right ballpark - so the refresh cannot silently regress.
"""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TRD = REPO / "sdlc-studio" / "trd.md"
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"

# Specific stale claims the review flagged - none may reappear.
FORBIDDEN = [
    "read-only over the workspace",
    "read-only-over-workspace",
    "(10 scripts)",
    "the 10 scripts",
    "181 tests",
    "status-cache.json",
]


class TrdFreshness(unittest.TestCase):
    def test_no_stale_claims(self) -> None:
        text = TRD.read_text(encoding="utf-8")
        present = [s for s in FORBIDDEN if s in text]
        self.assertEqual(present, [], f"stale TRD claim(s) reappeared: {present}")

    def test_script_count_claim_is_plausible(self) -> None:
        actual = len(list(SCRIPTS.glob("*.py")))
        text = TRD.read_text(encoding="utf-8")
        # the TRD states an approximate count ("40+ scripts"); assert reality is consistent
        m = re.search(r"(\d+)\+?\s+scripts", text)
        self.assertIsNotNone(m, "TRD no longer states a script count")
        claimed = int(m.group(1))
        self.assertGreaterEqual(actual, claimed, f"TRD claims {claimed}+ scripts, found {actual}")
        self.assertLess(claimed, actual + 20, "TRD script-count claim drifted far from reality")

    def test_write_contract_is_acknowledged(self) -> None:
        text = TRD.read_text(encoding="utf-8")
        self.assertIn("atomic_write", text)  # the real write surface is documented


class ThreatModelAgreesWithTheWriteContract(unittest.TestCase):
    """BG0187: 9's Threat Model called `plan.py archive` the SOLE write exception while
    5 rule 5 enumerates a dozen committed-file writers. Two sections of one document
    cannot describe the same contract differently."""

    def setUp(self) -> None:
        self.text = TRD.read_text(encoding="utf-8")

    def _threat_row(self) -> str:
        row = next((ln for ln in self.text.splitlines()
                    if "Script mutating files outside its remit" in ln), None)
        self.assertIsNotNone(row, "the Threat Model row has been renamed or removed")
        return row

    def test_the_threat_row_claims_no_sole_exception(self):
        self.assertNotRegex(self._threat_row(), r"sole,?\s+bounded\s+exception")
        self.assertNotIn("sole exception", self._threat_row())

    def test_the_threat_row_points_at_the_rule_that_enumerates_the_writers(self):
        self.assertRegex(self._threat_row(), r"rule\s*5")

    def test_rule_5_still_names_more_than_one_writer(self):
        # The contradiction is only resolved while rule 5 really is a SET. If it ever
        # narrows back to one writer, the threat row's plural wording becomes the wrong half.
        writers = ("artifact.py", "transition.py", "retro.py", "handoff.py", "decisions.py")
        present = [w for w in writers if w in self.text]
        self.assertGreater(len(present), 1,
                           f"rule 5 no longer enumerates a writer set: found {present}")


if __name__ == "__main__":
    unittest.main()
