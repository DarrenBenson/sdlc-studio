"""BG0995: refine strips the bold `**ACn**` label the skill's own filers write.

`file_finding.criteria_block` writes `- [ ] **ACn** text` and `artifact.py`'s story block
writes `**ACn:** text` (the colon inside the bold). The seed's label pattern wanted a separator
AFTER the closing bold, so neither stripped and a request the skill itself filed seeded
`### AC1: **AC1** text`, the BG0291 defect back for the house style. Each test drives
`refine.refine` over a throwaway workspace and reads the headings it seeded.
"""
from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import loader  # noqa: E402 - the canonical way to import a script under test
from lib import sdlc_md  # noqa: E402

refine = loader.load_script("refine")
file_finding = loader.load_script("file_finding")


def _seed(criteria_block: str) -> list[str]:
    """The `### AC` headings refine seeds onto a single story from a CR whose Acceptance
    Criteria section is `criteria_block`, verbatim."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "src").mkdir()
        (root / "src" / "a.py").write_text("", encoding="utf-8")
        cr = root / "sdlc-studio" / "change-requests" / "CR0001-x.md"
        cr.parent.mkdir(parents=True)
        cr.write_text("# CR-0001: CR0001\n\n> **Status:** Approved\n> **Priority:** P1\n"
                      "> **Type:** Improvement\n> **Size:** S\n> **Affects:** src/a.py\n\n"
                      "## Summary\n\ns\n\n## Acceptance Criteria\n\n"
                      f"{criteria_block}\n\n## Impact\n\ni\n", encoding="utf-8")
        res = refine.refine(root, "CR0001", "The epic", [("Only story", 3, None)],
                            skip_personas=True)
        text = sdlc_md.find_by_id(root, res["stories"][0])[0].read_text(encoding="utf-8")
    return [ln for ln in text.splitlines() if ln.startswith("### AC")]


class BoldAcLabelTests(unittest.TestCase):

    def test_every_filer_form_strips_to_one_label(self) -> None:
        # The two forms the filers write, then the BG0291 forms that already stripped.
        forms = [
            ("**AC1** the bare bold label", "### AC1: the bare bold label"),
            ("**AC2:** the colon inside the bold", "### AC2: the colon inside the bold"),
            ("**AC3**: the colon after the bold", "### AC3: the colon after the bold"),
            ("**AC4** - a dash after the bold", "### AC4: a dash after the bold"),
            ("AC5: the plain label", "### AC5: the plain label"),
            ("AC6) a bracket label", "### AC6: a bracket label"),
            ("**AC7.** a full stop inside the bold", "### AC7: a full stop inside the bold"),
            ("**ac8** a lower-case label", "### AC8: a lower-case label"),
        ]
        headings = _seed("\n".join(f"- [ ] {raw}" for raw, _ in forms))
        self.assertEqual(headings, [want for _, want in forms])
        for h in headings:
            with self.subTest(heading=h):
                self.assertEqual(len(re.findall(r"AC\d", h)), 1, "label repeated in heading")
                self.assertNotIn("*", h)

    def test_every_filer_form_strips_from_the_finding_filers_own_block(self) -> None:
        # Read from the writer itself, so a change to the filer's row shape is seen here.
        block = file_finding.criteria_block(
            "bug", {"acs": ["the gate refuses an unsigned run", "the report names the run"]})
        self.assertIn("**AC1**", block)
        self.assertEqual(_seed(block), ["### AC1: the gate refuses an unsigned run",
                                        "### AC2: the report names the run"])

    def test_every_filer_form_strips_and_a_non_label_bold_is_kept(self) -> None:
        # A bold run that only starts with an id is prose, not a label, and keeps its text;
        # so does a label with nothing after it, and an unspaced one.
        for kept in ("**AC1 is met** when the gate passes", "**AC1**", "**AC1**text",
                     "AC1** an unopened bold",
                     "the gate reports **AC2** unresolved", "AC1 with no separator"):
            with self.subTest(criterion=kept):
                self.assertEqual(refine._strip_ac_label(kept), kept)


if __name__ == "__main__":
    unittest.main()
