"""BG0887: the review command's examples show no per-document health percentage.

`reference-review.md` and `help/review.md` rendered each document's review as a bar at a
percentage (`PRD REVIEW ... 85%`) and the JSON sample carried `overall_health` and per-document
`health` keys, though nothing in the skill computes either. Each document section now shows the
finding count the review produces. A measured coverage figure beside its target is a
measurement, not a health score, and stays.
"""
# test-census-subject: .claude/skills/sdlc-studio/reference-review.md
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
DOCS = (SKILL / "reference-review.md", SKILL / "help" / "review.md")

_FENCE = re.compile(r"^```(\w*)\n(.*?)^```", re.M | re.S)
#: A document section's header in a dashboard sample: an unindented line naming the document.
_HEADER = re.compile(r"^\S+ (?:PRD|TRD|TSD|PERSONA) REVIEW\b|^\S+ TEST STRATEGY\b")
_FINDINGS = re.compile(r"\b\d+ findings?\b")


def _blocks(path: Path, lang: str) -> list[str]:
    return [body for tag, body in _FENCE.findall(path.read_text(encoding="utf-8")) if tag == lang]


class ReviewHealthDocsTests(unittest.TestCase):
    """AC1."""

    def test_no_document_health_percentage_is_shown(self) -> None:
        """MUTANTS: (1) restore `PRD REVIEW ... 85%` on one header; (2) restore
        `"overall_health": 85`; (3) a `"health"` key on one document; (4) drop a header's finding
        count. The control: the coverage rows measured against a target are still present."""
        headers = 0
        for doc in DOCS:
            for block in _blocks(doc, "text"):
                for line in block.splitlines():
                    if not _HEADER.search(line):
                        continue
                    headers += 1
                    self.assertNotRegex(line, r"\d+\s*%", f"{doc.name}: a document bar shows a percentage: {line}")
                    self.assertNotRegex(line, "[▓░]", f"{doc.name}: a document bar is still drawn: {line}")
                    self.assertRegex(line, _FINDINGS, f"{doc.name}: the header shows no finding count: {line}")
            for block in _blocks(doc, "json"):
                data = json.loads(block)
                self.assertNotIn("overall_health", data, f"{doc.name}: the JSON carries overall_health")
                for name, entry in (data.get("documents") or {}).items():
                    self.assertNotIn("health", entry, f"{doc.name}: documents.{name} carries a health key")
                    self.assertIsInstance(entry.get("findings"), int, f"{doc.name}: documents.{name} has no finding count")
        self.assertGreaterEqual(headers, 8, "the dashboard samples were not found, so nothing was judged")
        ref = DOCS[0].read_text(encoding="utf-8")
        self.assertIn("(target: 90%)", ref, "the measured coverage against its target was removed")
        self.assertIn("Coverage Target: 90% (Actual: 78%)", ref)


if __name__ == "__main__":
    unittest.main()
