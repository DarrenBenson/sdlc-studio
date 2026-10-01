"""BG0832: reference-review.md's persona consultation names sample roles, not a private project's.

Step 3a gave as its example one consuming project's consultation guide - its operator's first
name and three of its agent and service names - and the review JSON sample repeated one. The step
also named the amigos while loading only the project persona index, with no resolver. The shipped
text now names neutral sample roles and resolves the amigos through `persona_resolve.py`.
"""
from __future__ import annotations

# test-census-subject: .claude/skills/sdlc-studio/reference-review.md
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / ".claude" / "skills" / "sdlc-studio" / "reference-review.md"
#: The private names the step and the sample carried at HEAD.
PRIVATE = ("Darren", "Cora", "Webapp Dev", "HA")


def _section(text: str, heading: str) -> str:
    start = text.index(heading)
    nxt = text.find("\n### ", start + len(heading))
    return text[start:nxt if nxt != -1 else len(text)]


class ReviewConsultNeutralTests(unittest.TestCase):
    def test_step_3a_names_sample_roles(self) -> None:
        """AC1. MUTANT: HEAD's step 3a and JSON sample. MUTANT: neutralise the names but keep
        loading only the persona index - the step must name `persona_resolve.py` for the amigos."""
        text = DOC.read_text(encoding="utf-8")
        step = _section(text, "### 3a. Persona Consultation")
        sample = next(ln for ln in text.splitlines() if '"persona_artefacts"' in ln)
        for name in PRIVATE:
            pattern = re.compile(rf"\b{re.escape(name)}\b")
            self.assertIsNone(pattern.search(step), f"step 3a still names {name!r}")
            self.assertIsNone(pattern.search(sample), f"the JSON sample still names {name!r}")
        self.assertIn("persona_resolve.py resolve-consult", step)


if __name__ == "__main__":
    unittest.main()
