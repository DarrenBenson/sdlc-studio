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


if __name__ == "__main__":
    unittest.main()
