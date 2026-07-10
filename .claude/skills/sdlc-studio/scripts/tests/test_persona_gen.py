"""Unit tests for persona_gen.py - the deterministic floor of team generation.

The load-bearing contract is never-clobber: authored vs generated is discriminated by the
provenance stamp PLUS a content hash, so an operator's edit to a generated card promotes it
to authored (a re-run may never overwrite it).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


pg = _load("persona_gen")

CARD = ("<!-- role: qa -->\n# Priya Sharma - QA seat\n\n## Who They Are\n\n"
        "Payments QA, paranoid about idempotency.\n\n## Lens\n\nx\n"
        "## Pushes Back When\n\nx\n## Shadow\n\nx\n")


class StampClassifyTests(unittest.TestCase):
    def _card(self, root: Path, name: str = "priya.md", body: str = CARD) -> Path:
        d = root / "sdlc-studio" / "personas" / "seats"
        d.mkdir(parents=True, exist_ok=True)
        p = d / name
        p.write_text(body, encoding="utf-8")
        return p

    def test_unstamped_card_is_authored(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(pg.classify(self._card(Path(d))), "authored")

    def test_stamped_card_is_generated_pristine(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = self._card(Path(d))
            self.assertEqual(pg.stamp(p), "generated-pristine")
            text = p.read_text(encoding="utf-8")
            self.assertIn("provisional-unverified", text)
            # the stamp sits beside the role comment, not at EOF
            self.assertLess(text.index("provenance:"), text.index("# Priya"))

    def test_operator_edit_promotes_to_authored_semantics(self) -> None:
        # The critic's condition: stamp present but hash mismatch = generated-edited,
        # which never-clobber must treat as authored.
        with tempfile.TemporaryDirectory() as d:
            p = self._card(Path(d))
            pg.stamp(p)
            p.write_text(p.read_text(encoding="utf-8").replace(
                "paranoid about idempotency", "paranoid about idempotency AND settlement"),
                encoding="utf-8")
            self.assertEqual(pg.classify(p), "generated-edited")

    def test_restamp_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = self._card(Path(d))
            pg.stamp(p)
            first = p.read_text(encoding="utf-8")
            pg.stamp(p)  # regenerate-then-restamp path
            self.assertEqual(p.read_text(encoding="utf-8"), first)  # no stamp stacking

    def test_accept_clears_label_and_records_date(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = self._card(Path(d))
            pg.stamp(p)
            self.assertTrue(pg.accept(p, today="2026-07-10"))
            text = p.read_text(encoding="utf-8")
            self.assertNotIn("provisional-unverified", text)
            self.assertIn("provenance: reviewed 2026-07-10", text)
            self.assertEqual(pg.classify(p), "authored")   # accepted = authored from here
            self.assertFalse(pg.accept(p))                  # idempotent: nothing to clear

    def test_stamp_refuses_over_a_reviewed_marker(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = self._card(Path(d))
            pg.stamp(p)
            pg.accept(p, today="2026-07-10")
            with self.assertRaises(ValueError):
                pg.stamp(p)  # an accepted card is not silently regenerated over

    def test_provisional_seats_lists_both_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seat = self._card(root)
            sd = root / "sdlc-studio" / "personas" / "stakeholders"
            sd.mkdir(parents=True)
            stake = sd / "omar.md"
            stake.write_text("# Omar - buyer\n", encoding="utf-8")
            pg.stamp(seat)
            pg.stamp(stake)
            pg.accept(seat)
            self.assertEqual(pg.provisional_seats(root), ["stakeholders/omar.md"])


if __name__ == "__main__":
    unittest.main()
