"""US0073/CR0178: the benchmark protocol is pre-registered with the required sections, so a
later measured run cannot quietly reshape it."""
import unittest
from pathlib import Path

PROTOCOL = Path(__file__).resolve().parents[2] / "docs" / "benchmarks" / "protocol.md"

REQUIRED = ["Arms", "Task set", "Metrics", "Sample size", "Publication"]


class BenchmarkProtocol(unittest.TestCase):
    def test_protocol_exists_and_is_complete(self) -> None:
        self.assertTrue(PROTOCOL.exists(), "benchmark protocol not pre-registered")
        text = PROTOCOL.read_text(encoding="utf-8")
        missing = [s for s in REQUIRED if s not in text]
        self.assertEqual(missing, [], f"protocol missing sections: {missing}")

    def test_commits_to_publishing_and_a_real_baseline(self) -> None:
        text = PROTOCOL.read_text(encoding="utf-8").lower()
        self.assertIn("regardless", text)          # publish regardless of outcome
        self.assertIn("held-back", text)           # oracle-measured defect escapes
        self.assertIn("not the harness author", text)  # non-straw-man baseline


PROTOCOL_V2 = PROTOCOL.parent / "protocol-v2.md"

V2_REQUIRED = ["Questions", "Arms", "Task set", "Metrics", "Sample size", "Analysis",
               "cut order"]


class BenchmarkProtocolV2(unittest.TestCase):
    """CR0193/US0089: v2 is a superseding pre-registration, not an in-place edit of v1."""

    def test_v2_exists_and_is_complete(self) -> None:
        self.assertTrue(PROTOCOL_V2.exists(), "protocol v2 not pre-registered")
        text = PROTOCOL_V2.read_text(encoding="utf-8")
        missing = [s for s in V2_REQUIRED if s not in text]
        self.assertEqual(missing, [], f"protocol v2 missing sections: {missing}")

    def test_v2_commitments(self) -> None:
        text = PROTOCOL_V2.read_text(encoding="utf-8").lower()
        self.assertIn("regardless", text)          # publish regardless of outcome
        self.assertIn("held-back", text)           # oracle-scored defect escapes
        self.assertIn("supersedes", text)          # openly supersedes v1, no silent amend
        # the Auditability metric scores outcomes, never tool-artifact presence
        self.assertIn("never artifact presence", text)
        # reviewer-independence carries no weight (a by-construction arm-A point otherwise)
        self.assertIn("weight 0", text)

    def test_v1_records_the_supersession(self) -> None:
        text = PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("protocol-v2.md", text)


if __name__ == "__main__":
    unittest.main()
