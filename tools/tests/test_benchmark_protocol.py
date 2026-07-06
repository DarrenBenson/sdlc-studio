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


if __name__ == "__main__":
    unittest.main()
