"""BG1404: `critic.py record` splits a verdict's issues at every unescaped `;`, so a finding
written with a semicolon inside it leaves an untagged tail that is refused as carrying no origin.
The split and its `\\;` escape stay as they are; the refusal now names the escape, on the flag
and on the verdict file a reviewer returns.

Each case drives `critic.py record` through its entry point in a throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
CRITIC = SCRIPTS / "critic.py"
critic = loader.load_script("critic")
UNIT = "US0101"
ESCAPE = "write \\; to keep a semicolon inside one finding"
WHY = "An unescaped ';' can end a finding"


def _project(root: Path) -> None:
    story = root / "sdlc-studio" / "stories" / f"{UNIT}-widget.md"
    story.parent.mkdir(parents=True)
    story.write_text(f"# {UNIT}: widget\n\n> **Status:** Review\n> **Points:** 1\n"
                     f"> **Epic:** EP0001\n> **Affects:** src/widget.py\n\n"
                     "## Acceptance Criteria\n\n### AC1: works\n- **Verify:** shell true\n",
                     encoding="utf-8")


def _record(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(CRITIC), "record", "--unit", UNIT,
                           "--reviewer", "qa-seat", "--author", "eng-seat", *args,
                           "--root", str(root)],
                          capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                          check=False)


class IssuesSemicolonTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        _project(self.root)

    def _refused_naming_the_escape(self, r: subprocess.CompletedProcess) -> None:
        self.assertEqual(2, r.returncode, r.stderr)
        self.assertIn("carry no origin", r.stderr)
        self.assertIn(ESCAPE, r.stderr, f"the refusal does not name the escape:\n{r.stderr}")
        self.assertIn(WHY, r.stderr, f"the refusal does not say why the tail was cut:\n{r.stderr}")
        self.assertEqual([], critic.read_verdicts(self.root), "a refused record wrote a row")

    def test_the_origin_refusal_names_the_escape(self) -> None:
        """AC1. Mutants: the refusal without the escape's sentence, or without the reason an
        unescaped `;` cut the finding."""
        self._refused_naming_the_escape(_record(self.root, "--verdict", "reject",
                                                "--issues", "[new] a; b"))

    def test_the_from_verdict_refusal_names_the_escape(self) -> None:
        """AC2: the verdict file a reviewer returns reaches the same refusal."""
        verdict = self.root / "verdict.txt"
        verdict.write_text("VERDICT: REJECT\nISSUES: [new] a; b\nBLOCKING: none\n",
                           encoding="utf-8")
        self._refused_naming_the_escape(_record(self.root, "--from-verdict", str(verdict)))

    def test_an_escaped_semicolon_keeps_one_finding(self) -> None:
        """AC3, the control: the split and the escape are unchanged."""
        r = _record(self.root, "--verdict", "reject", "--issues", "[new] a\\; b")
        self.assertEqual(0, r.returncode, r.stderr)
        rows = critic.read_verdicts(self.root)
        self.assertEqual(1, len(rows))
        self.assertEqual([{"origin": "new", "text": "a; b"}],
                         critic.parse_findings(rows[0]["issues"]))


if __name__ == "__main__":
    unittest.main()
