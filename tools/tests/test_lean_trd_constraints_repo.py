"""US0932: this repository's TRD constraints reach a lane brief.

The Must Have constraints that govern one component sit in that component's Constraints cell of
the TRD's Component Overview, so `sprint.py lane brief` hands them to the agent building a unit
that touches the component. This module reads the repository's own `sdlc-studio/trd.md` and
drives the shipped entry point against a copy of it in a throwaway tree.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
TRD = REPO / "sdlc-studio" / "trd.md"

sys.path.insert(0, str(SCRIPTS))
import sprint  # noqa: E402

SDLC_MD = ".claude/skills/sdlc-studio/scripts/lib/sdlc_md.py"
SOURCE_OF_TRUTH = "`lib/sdlc_md.py` remains the single source of truth for markdown conventions"


class TrdConstraintsRepoTests(unittest.TestCase):
    def test_this_repos_trd_constraints_reach_a_brief(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "stories").mkdir(parents=True)
            (root / "sdlc-studio" / "trd.md").write_text(TRD.read_text(encoding="utf-8"),
                                                         encoding="utf-8")
            (root / "sdlc-studio" / "stories" / "US0001-x.md").write_text(
                f"# US0001: a change\n\n> **Status:** Ready\n"
                f"> **Affects:** {SDLC_MD}, .claude/skills/sdlc-studio/SKILL.md\n"
                "> **Points:** 2\n\n## Acceptance Criteria\n\n### AC1: it holds\n\n"
                "- **Verify:** shell true\n", encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = sprint.main(["lane", "brief", "--units", "US0001", "--root", str(root)])
        self.assertEqual(0, rc, err.getvalue())
        brief = out.getvalue()
        self.assertIn("TRD constraints on the components this unit touches:", brief)
        self.assertIn(f"`scripts/lib/`: {SOURCE_OF_TRUTH}", brief)
        # The router and the script layer each carry their own Must Have constraint too.
        self.assertRegex(brief, r"\n  `SKILL\.md` router: \S")
        self.assertRegex(brief, r"\n  `scripts/` \(60\+ scripts\): \S")
        # Stated once: the per-component rule has moved out of section 13, not been copied.
        must_have = TRD.read_text(encoding="utf-8").split("### Must Have", 1)[1]
        must_have = must_have.split("\n### ", 1)[0]
        self.assertNotIn("single source of truth", must_have)


if __name__ == "__main__":
    unittest.main()
