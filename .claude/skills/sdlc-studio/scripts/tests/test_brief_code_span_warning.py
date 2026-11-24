"""BG1450: a reviewer's verdict file is refused by `critic.py record` when a code span in it
begins or ends with whitespace (markdownlint's MD038), and no brief told the reviewer so. The
return contract every brief ends on, first round at either tier and the `--rejoinder` re-review,
now states the rule.

Each case drives `critic.py brief` through its entry point in a throwaway project.
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

SCRIPTS = Path(__file__).resolve().parent.parent
CRITIC = SCRIPTS / "critic.py"
UNIT = "US0101"
CONTRACT = "Return EXACTLY"
RULE = "A code span must not begin or end with whitespace"


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _project(root: Path) -> None:
    _write(root, "src/widget.py", "def w():\n    return 1\n")
    _write(root, "sdlc-studio/personas/seats/qa.md",
           "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n\n## Lens\n\nx\n\n"
           "## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")
    _write(root, f"sdlc-studio/stories/{UNIT}-widget.md",
           f"# {UNIT}: widget\n\n> **Status:** Review\n> **Points:** 1\n> **Epic:** EP0001\n"
           f"> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
           "- **Verify:** shell true\n")


def _brief(root: Path, *extra: str) -> str:
    r = subprocess.run([sys.executable, "-B", str(CRITIC), "brief", "--unit", UNIT, "--seat",
                        "qa", *extra, "--root", str(root)],
                       capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                       check=False)
    assert r.returncode == 0, r.stderr
    return r.stdout


def _contract(brief: str) -> str:
    """The return contract the brief ends on: from its last opening line to the end."""
    at = brief.rfind(CONTRACT)
    assert at >= 0, f"no return contract in the brief:\n{brief[-2000:]}"
    return " ".join(brief[at:].split())


class BriefCodeSpanWarningTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        _project(self.root)

    def test_the_return_contract_states_the_code_span_rule(self) -> None:
        """AC1. Mutant: the contract without the rule."""
        contract = _contract(_brief(self.root, "--tier", "full"))
        self.assertIn(RULE, contract)
        self.assertIn("MD038", contract, "the rule does not name the check that refuses it")

    def test_every_brief_kind_states_the_code_span_rule(self) -> None:
        """AC2: the light brief and the rejoinder end on the same contract, so neither is
        silent. Mutant: the rule placed in one tier's section only."""
        prior = self.root / "prior.txt"
        prior.write_text("VERDICT: REJECT\nISSUES: [new] w is wrong\nBLOCKING: w is wrong\n",
                         encoding="utf-8")
        for kind, extra in (("light", ("--tier", "light")),
                            ("rejoinder", ("--tier", "full", "--rejoinder", str(prior)))):
            with self.subTest(kind=kind):
                brief = _brief(self.root, *extra)
                if kind == "rejoinder":
                    self.assertIn("RE-REVIEW (rejoinder)", brief, "premise: not a rejoinder")
                    self.assertLess(brief.find("RE-REVIEW (rejoinder)"), brief.rfind(CONTRACT),
                                    "premise: the contract read is the base brief's")
                self.assertIn(RULE, _contract(brief))


if __name__ == "__main__":
    unittest.main()
