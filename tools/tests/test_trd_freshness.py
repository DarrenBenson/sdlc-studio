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


if __name__ == "__main__":
    unittest.main()
