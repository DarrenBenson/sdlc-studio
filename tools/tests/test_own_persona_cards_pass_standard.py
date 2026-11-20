"""This repository's own persona and seat cards break no blocking rule of the persona standard,
so the refusal that stops a card breaking one from framing a brief never stops this repository's
own review briefs, refine panels or triage panels. Reads the cards on disk, never a fixture."""
from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import persona_resolve  # noqa: E402
import persona_review  # noqa: E402

PERSONAS = REPO / "sdlc-studio" / "personas"
SEATS = PERSONAS / "seats"


class OwnPersonaCardsTests(unittest.TestCase):

    def test_this_repositorys_cards_break_no_blocking_rule(self) -> None:
        """AC5. Mutants: a demographic token in one of this repository's seat cards; the check
        run over a fixture, or over no card, in place of this repository's own."""
        seats = sorted(p.resolve() for p in SEATS.glob("*.md"))
        personas = sorted(p.resolve() for p in PERSONAS.glob("*.md")
                          if p.name.lower() not in ("index.md", "readme.md", "consult-guide.md")
                          and not p.name.startswith("_"))
        self.assertEqual(["engineering.md", "product.md", "qa.md"], [p.name for p in seats],
                         "premise: this repository's three seat cards are read")
        self.assertTrue(personas, "premise: this repository's persona cards are read")
        self.assertEqual(seats + personas,
                         sorted(p.resolve() for p in persona_review._seat_cards(REPO))
                         + sorted(p.resolve() for p in persona_review._persona_cards(REPO)),
                         "premise: the check reads these cards and no others")
        findings = persona_review.check(REPO)
        self.assertTrue({str(p) for p in seats + personas} >= {f["file"] for f in findings},
                        "every finding sits on one of this repository's own cards")
        blocked = [f"{Path(f['file']).relative_to(REPO)}: {f['rule']}: {f['message']}"
                   for f in findings if f["severity"] == persona_review.BLOCKS]
        self.assertEqual([], blocked)
        for card in seats + personas:
            with self.subTest(card=card.name):
                self.assertEqual([], persona_review.blocking(REPO, card))
        # So each seat a review brief, a refine panel or a triage panel resolves frames from
        # this repository's own card, unrefused.
        for role in sorted({*persona_resolve.REFINE_PANEL, *persona_resolve.TRIAGE_PANEL}):
            with self.subTest(role=role), redirect_stderr(io.StringIO()):
                self.assertEqual(SEATS / f"{role}.md", persona_resolve.review_card(REPO, role))
                self.assertEqual(SEATS / f"{role}.md", persona_resolve.resolve_consult(REPO, role))


if __name__ == "__main__":
    unittest.main()
