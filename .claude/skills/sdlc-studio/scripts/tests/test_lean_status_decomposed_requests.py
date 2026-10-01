"""BG0869: `status.py backlog` lists a decomposed request as in delivery, not awaiting refinement.

After every open CR here was decomposed, the backlog still printed six of them under 'refine
requests / triage issues before it is work'. A request with children is delivered through them;
the child test is the one `status.discovery_awaiting` already applies. Each test drives the
shipped CLI as a subprocess against a throwaway tree.
"""
from __future__ import annotations

# test-census-subject: .claude/skills/sdlc-studio/scripts/status.py
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class StatusDecomposedRequestTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        sd = self.root / "sdlc-studio"
        _write(sd / "change-requests" / "CR0001-decomposed.md",
               "# CR0001: decomposed\n\n> **Status:** In Progress\n"
               "> **Decomposed-into:** EP0001\n")
        _write(sd / "change-requests" / "CR0002-fresh.md",
               "# CR0002: fresh\n\n> **Status:** Proposed\n")
        _write(sd / "epics" / "EP0001-delivery.md",
               "# EP0001: delivery\n\n> **Status:** In Progress\n> **Parent:** CR0001\n")
        _write(sd / "stories" / "US0001-a-story.md",
               "# US0001: a story\n\n> **Status:** Ready\n> **Epic:** EP0001\n> **Points:** 1\n")

    def _backlog(self) -> str:
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "status.py"), "backlog", "--root",
             str(self.root)], capture_output=True, text=True, check=False, timeout=120)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        return proc.stdout

    def test_a_decomposed_request_is_not_listed_as_awaiting_refinement(self) -> None:
        """AC1. MUTANT: HEAD, which lists CR0001 beside CR0002 under the refine heading.
        MUTANT: drop the decomposed request altogether - it must still be shown, with its
        epic, so the census of open requests is unchanged."""
        out = self._backlog()
        disc = out[out.index("Discovery backlog"):out.index("Delivery backlog")]
        heading, _, rest = disc.partition("\n")
        awaiting, _, delivering = rest.partition("in delivery")
        self.assertIn("CR0002", awaiting)
        self.assertNotIn("CR0001", awaiting, "a decomposed request is listed as awaiting refine")
        self.assertTrue(heading.rstrip().endswith(": 1"), heading)
        self.assertIn("CR0001", delivering, "the decomposed request is no longer shown")
        self.assertIn("EP0001", delivering, "its epic is not named")
        self.assertIn("Backlog: 4 non-terminal artefact(s)", out)


if __name__ == "__main__":
    unittest.main()
