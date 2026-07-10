"""Unit tests for persona_resolve.py (RFC0020 D7: most-specific-first worker identity)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "persona_resolve.py"


def _load():
    spec = importlib.util.spec_from_file_location("persona_resolve", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["persona_resolve"] = mod
    spec.loader.exec_module(mod)
    return mod


def _project_amigo(root: Path, seat: str, text: str) -> Path:
    d = root / "sdlc-studio" / "personas" / "amigos"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{seat}.md"
    p.write_text(text, encoding="utf-8")
    return p


def _seat(root: Path, filename: str, text: str) -> Path:
    d = root / "sdlc-studio" / "personas" / "seats"
    d.mkdir(parents=True, exist_ok=True)
    p = d / filename
    p.write_text(text, encoding="utf-8")
    return p


# A minimal seat card with a declared role and the three review-render sections present.
def _seat_body(role: str, name: str = "Sarah") -> str:
    return (f"<!-- role: {role} -->\n# {name} - {role} seat\n\n"
            "## Lens\n\nx\n## Pushes Back When\n\nx\n## Shadow\n\nx\n")


class ResolutionTests(unittest.TestCase):
    def test_default_card_used_when_no_project_override(self) -> None:
        # The skill ships engineering.md, so with no project override the default resolves.
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            card = mod.resolve_card(Path(d), "engineering")
            self.assertIsNotNone(card)
            self.assertEqual(card.name, "engineering.md")
            self.assertIn("templates", str(card))  # the skill default, not a project copy

    def test_project_override_wins(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mine = _project_amigo(root, "engineering", "# My staff frontend engineer\n")
            card = mod.resolve_card(root, "engineering")
            self.assertEqual(card, mine)  # most-specific-first: project beats default

    def test_skip_personas_is_generic(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(mod.resolve_card(Path(d), "engineering", skip_personas=True))

    def test_frame_empty_for_generic_byte_equivalent(self) -> None:
        # --skip-personas must yield a byte-equivalent contract: the framing is empty.
        mod = _load()
        self.assertEqual(mod.frame(None, "engineering", "build"), "")

    def test_frame_appends_contract_is_law(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mine = _project_amigo(root, "qa", "# Sam\n\nthe QA charter body\n")
            out = mod.frame(mine, "qa", "review")
            self.assertIn("the QA charter body", out)        # the card is included
            self.assertIn("is law", out)                     # contract-is-law guard
            self.assertIn("separate instance", out)          # independence reminder
            self.assertIn("review render", out)              # the requested render

    def test_unknown_seat_exits_nonzero(self) -> None:
        mod = _load()
        self.assertEqual(mod.main(["resolve", "--seat", "marketing"]), 2)

    def test_cli_path_only_prints_resolved_path(self) -> None:
        import io
        from contextlib import redirect_stdout
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mine = _project_amigo(root, "product", "# Lena\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = mod.main(["resolve", "--seat", "product", "--root", str(root), "--path-only"])
            self.assertEqual(rc, 0)
            self.assertEqual(buf.getvalue().strip(), str(mine))


class RoleFieldTests(unittest.TestCase):
    """The declared role field (RFC0021 D6): the resolver keys on it, never H1 prose or filename."""

    def test_card_role_reads_declared_field(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            p = _seat(Path(d), "sarah.md", _seat_body("engineering"))
            self.assertEqual(mod.card_role(p), "engineering")

    def test_card_role_ignores_h1_prose(self) -> None:
        # The H1 says "Engineering" but the declared role is qa - the field wins, not the prose.
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            p = _seat(Path(d), "marcus.md",
                      "<!-- role: qa -->\n# Marcus - Engineering lead\n\n"
                      "## Lens\n\nx\n## Pushes Back When\n\nx\n## Shadow\n\nx\n")
            self.assertEqual(mod.card_role(p), "qa")

    def test_card_role_none_when_undeclared(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            p = _seat(Path(d), "nobody.md", "# Nobody - just prose\n\n## Lens\n\nx\n")
            self.assertIsNone(mod.card_role(p))

    def test_default_cards_declare_their_role(self) -> None:
        # The shipped defaults carry a machine-readable role, not just an H1.
        mod = _load()
        for seat in ("engineering", "qa", "product"):
            card = mod.default_card(seat)
            self.assertIsNotNone(card, seat)
            self.assertEqual(mod.card_role(card), seat)


class SeatResolutionTests(unittest.TestCase):
    """BG0042 / RFC0021 D6: the resolver reads role-matched seats, not just amigos/."""

    def test_role_matched_seat_resolves_over_default(self) -> None:
        # The load-bearing BG0042 AC: a project seat (no amigo override) must beat the skill default.
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seat = _seat(root, "sarah.md", _seat_body("engineering"))
            card = mod.resolve_card(root, "engineering")
            self.assertEqual(card, seat)  # the authored seat, not Dani the default

    def test_declared_seat_beats_amigo_override(self) -> None:
        # CR0218 converged home: the declared-role seat is THE project authority; the
        # legacy personas/amigos/<seat>.md file no longer shadows it (the old amigos-first
        # order buried every authored/generated seat on upgraded projects).
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seat = _seat(root, "sarah.md", _seat_body("engineering"))
            _project_amigo(root, "engineering", "<!-- role: engineering -->\n# Mine\n")
            self.assertEqual(mod.resolve_card(root, "engineering"), seat)

    def test_zero_claim_role_falls_through_to_default(self) -> None:
        # No seat declares the role -> fall through to the skill default, never crash (D6).
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seat(root, "sarah.md", _seat_body("qa"))  # qa seat present, engineering absent
            card = mod.resolve_card(root, "engineering")
            self.assertIsNotNone(card)
            self.assertIn("templates", str(card))  # fell through to the default, not the qa seat

    def test_two_claim_role_is_deterministic_lexical(self) -> None:
        # Two seats declare engineering -> deterministic lexical-by-filename pick, no crash (D6).
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seat(root, "zoe.md", _seat_body("engineering", "Zoe"))
            first = _seat(root, "anna.md", _seat_body("engineering", "Anna"))
            self.assertEqual(mod.resolve_card(root, "engineering"), first)  # anna.md < zoe.md

    def test_two_claim_role_warns(self) -> None:
        # The ambiguity must surface a warning, not resolve silently (D6).
        import io
        from contextlib import redirect_stderr
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seat(root, "zoe.md", _seat_body("engineering", "Zoe"))
            _seat(root, "anna.md", _seat_body("engineering", "Anna"))
            buf = io.StringIO()
            with redirect_stderr(buf):
                mod.resolve_card(root, "engineering")
            self.assertIn("engineering", buf.getvalue())
            self.assertIn("anna.md", buf.getvalue())

    def test_render_less_review_seat_is_hard_error(self) -> None:
        # RFC0021 D4: a resolved seat lacking its review render is a HARD ERROR for --render review,
        # not a silent fallback to the generic default.
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seat(root, "sarah.md", "<!-- role: engineering -->\n# Sarah\n\nno review sections\n")
            with self.assertRaises(mod.RenderError):
                mod.resolve_card(root, "engineering", render="review")

    def test_render_less_seat_ok_for_build(self) -> None:
        # The hard error is render-scoped: a build render does not require the review sections.
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seat = _seat(root, "sarah.md", "<!-- role: engineering -->\n# Sarah\n\nbuild only\n")
            self.assertEqual(mod.resolve_card(root, "engineering", render="build"), seat)


class IndependenceFloorTests(unittest.TestCase):
    """RFC0021 D5: build and review of ONE seat card are separate instances."""

    def test_build_and_review_both_carry_independence_note(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seat = _seat(root, "sarah.md", _seat_body("engineering"))
            build = mod.frame(seat, "engineering", "build")
            review = mod.frame(seat, "engineering", "review")
            for out in (build, review):
                self.assertIn("separate instance", out)
                self.assertIn("never sign off your own work", out)

    def test_critic_requires_author_differs_even_from_one_card(self) -> None:
        # Build and review framed from one seat card are distinct delegation instances; the critic
        # gate still demands author != reviewer. One id (a self-review) is NOT independent.
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "critic", SCRIPT.parent / "critic.py")
        critic = importlib.util.module_from_spec(spec)
        sys.modules["critic"] = critic
        spec.loader.exec_module(critic)
        # two instances of the one seat -> independent
        self.assertTrue(critic.is_independent(
            {"author": "sarah-build-7", "reviewer": "sarah-review-9"}))
        # one shared instance (signed off own work) -> NOT independent
        self.assertFalse(critic.is_independent(
            {"author": "sarah-build-7", "reviewer": "sarah-build-7"}))


class ConsultResolutionTests(unittest.TestCase):
    """CR0124: consult resolves its seat through the same declared-`role:` chain as delegation,
    so an authored seat is honoured in consult, not only in delegation."""

    def test_consult_resolves_authored_seat_over_generic(self) -> None:
        # The load-bearing CR0124 AC: a project seat (role-matched) drives the consult, not the
        # generic enriched seat schema.
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seat = _seat(root, "sarah.md", _seat_body("engineering"))
            card = mod.resolve_consult(root, "engineering")
            self.assertEqual(card, seat)  # the authored seat, not the generic template

    def test_consult_falls_back_to_generic_schema_when_no_seat(self) -> None:
        # No seat fills the role and no default exists -> the generic enriched seat schema is the
        # fallback (the consult still has a charter to run against).
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            card = mod.resolve_consult(root, "ux")  # a role the skill ships no default for
            self.assertIsNotNone(card)
            self.assertEqual(card.name, "amigo-template.md")  # the generic schema fallback

    def test_consult_uses_skill_default_when_no_authored_seat(self) -> None:
        # A role the skill ships a default for, with no authored seat -> the default seat, not the
        # bare generic schema.
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            card = mod.resolve_consult(root, "engineering")
            self.assertIsNotNone(card)
            self.assertEqual(card.name, "engineering.md")
            self.assertIn("templates", str(card))

    def test_consult_render_less_seat_is_hard_error(self) -> None:
        # RFC0021 D4: a consult needs the review render; a render-less authored seat is a hard error,
        # never a silent fallback to the generic schema.
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seat(root, "sarah.md", "<!-- role: engineering -->\n# Sarah\n\nno review sections\n")
            with self.assertRaises(mod.RenderError):
                mod.resolve_consult(root, "engineering")

    def test_consult_cli_path_only_prints_authored_seat(self) -> None:
        import io
        from contextlib import redirect_stdout
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seat = _seat(root, "sarah.md", _seat_body("engineering"))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = mod.main(["resolve-consult", "--role", "engineering",
                               "--root", str(root), "--path-only"])
            self.assertEqual(rc, 0)
            self.assertEqual(buf.getvalue().strip(), str(seat))


class ConvergedHomeTests(unittest.TestCase):
    """CR0218 (RFC0021 D2, Dani's blocking consult finding): personas/seats/ is THE runtime
    home. A role-claiming seat card must beat the legacy personas/amigos/<seat>.md file -
    the old amigos-first order silently shadowed every authored/generated seat on upgraded
    projects. The legacy path stays as a warned fallback, never the winner."""

    def test_declared_seat_beats_legacy_amigos_file(self) -> None:
        pr = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project_amigo(root, "qa", _seat_body("qa", "Generic Sam"))
            authored = _seat(root, "priya.md", _seat_body("qa", "Priya"))
            card = pr.resolve_card(root, "qa")
            self.assertEqual(card, authored)  # seats/ wins; amigos/ no longer shadows

    def test_legacy_amigos_fallback_warns(self) -> None:
        pr = _load()
        import io
        from contextlib import redirect_stderr
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            legacy = _project_amigo(root, "qa", _seat_body("qa", "Old Sam"))
            err = io.StringIO()
            with redirect_stderr(err):
                card = pr.resolve_card(root, "qa")
            self.assertEqual(card, legacy)          # still resolves (back-compat)
            self.assertIn("legacy", err.getvalue()) # but says migrate to seats/
            self.assertIn("seats/", err.getvalue())


if __name__ == "__main__":
    unittest.main()
