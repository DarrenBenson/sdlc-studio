"""US1089: this repository blocks a brief whose author has recorded no self-check, and says so.

The shipped default for `review.author_self_check` is `report`, so a consuming project is not
refused on its first review after an upgrade; this repository sets `block`. AGENTS.md's rule to
exercise every claim before asking for review names the gate that now holds it, and no longer
calls itself ungated. This module reads the repository's own files, so it lives here, where
nothing installs.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
# test-census-subject: AGENTS.md
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"

sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402

LEAD = "**Exercise every claim through the shipped entry point before asking for review.**"


def _paragraph(text: str, lead: str) -> str:
    """The blank-line-delimited paragraph of `text` that starts with `lead`; "" when none does."""
    return next((p for p in re.split(r"\n[ \t]*\n", text) if p.strip().startswith(lead)), "")


class AuthorSelfCheckRepoTests(unittest.TestCase):

    def test_this_repository_blocks_and_says_so(self) -> None:
        """AC5. Mutants: this repository's config left at the default, so its briefs are only
        reported on; AGENTS.md keeping 'Ungated until CR0520 ships `verify_ac lane-check`'
        beside the new names, or not naming the record command and the setting."""
        self.assertEqual("block", critic.author_self_check_mode(REPO),
                         "sdlc-studio/.config.yaml does not set review.author_self_check: block")
        para = _paragraph((REPO / "AGENTS.md").read_text(encoding="utf-8"), LEAD)
        self.assertTrue(para, "AGENTS.md has no paragraph led by the exercise-every-claim rule")
        for name in ("critic.py self-check record", "review.author_self_check"):
            self.assertIn(name, para, f"the rule does not name {name}")
        for retired in ("CR0520", "lane-check"):
            self.assertNotIn(retired, para, f"the rule still names {retired}")


if __name__ == "__main__":
    unittest.main()
