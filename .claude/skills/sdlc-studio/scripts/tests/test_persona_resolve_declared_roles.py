"""`persona_resolve.py resolve --seat` takes a role a project seat card declares, as
`critic.py brief --seat` does, and refuses only a role no card declares and the skill does not
ship."""
from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "persona_resolve.py"


def _load():
    spec = importlib.util.spec_from_file_location("persona_resolve", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["persona_resolve"] = mod
    spec.loader.exec_module(mod)
    return mod


def _seat(root: Path, filename: str, text: str) -> Path:
    d = root / "sdlc-studio" / "personas" / "seats"
    d.mkdir(parents=True, exist_ok=True)
    p = d / filename
    p.write_text(text, encoding="utf-8")
    return p


SRE_CARD = ("<!-- role: sre -->\n# Priya Shah - SRE amigo\n\nthe sre charter body\n\n"
            "## Lens\n\nx\n## Pushes Back When\n\nx\n## Shadow\n\nx\n")


def _run(mod, argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = mod.main(argv)
    return rc, out.getvalue(), err.getvalue()


class DeclaredRoleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.card = _seat(self.root, "priya.md", SRE_CARD)

    def test_a_declared_sre_seat_resolves(self) -> None:
        rc, out, err = _run(self.mod, ["resolve", "--seat", "sre", "--root", str(self.root)])
        self.assertEqual(rc, 0, err)
        self.assertNotIn("unknown seat", err)
        self.assertIn("You are the sre amigo", out)
        self.assertIn("the sre charter body", out)  # framed from the project's own card
        rc, out, err = _run(self.mod, ["resolve", "--seat", "sre", "--root", str(self.root),
                                       "--path-only"])
        self.assertEqual(rc, 0, err)
        self.assertEqual(out.strip(), str(self.card))
        rc, out, err = _run(self.mod, ["resolve", "--seat", "sre", "--root", str(self.root),
                                       "--render", "review", "--format", "json"])
        self.assertEqual(rc, 0, err)
        self.assertIn('"seat": "sre"', out)
        self.assertIn(str(self.card), out)

    def test_an_undeclared_role_is_refused(self) -> None:
        _seat(self.root, "nameless.md", "# Nameless - a card with no role line\n")
        rc, out, err = _run(self.mod, ["resolve", "--seat", "security", "--root", str(self.root)])
        self.assertEqual(rc, 2)
        self.assertEqual(out, "")
        self.assertIn("unknown seat 'security'", err)
        # the refusal names every role the project can resolve: the shipped three and its own
        self.assertIn("engineering, qa, product, sre", err)
        # and the card that declares no role, which is why no role it meant is listed
        self.assertIn("nameless.md declares no role", err)

    def test_a_shipped_seat_still_resolves_with_no_project_card(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rc, out, err = _run(self.mod, ["resolve", "--seat", "qa", "--root", d, "--path-only"])
        self.assertEqual(rc, 0, err)
        self.assertIn("templates", out)  # the skill's shipped card, the zero-setup default

    def test_a_declared_role_from_another_project_is_refused_here(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rc, _out, err = _run(self.mod, ["resolve", "--seat", "sre", "--root", d])
        self.assertEqual(rc, 2)
        self.assertIn("unknown seat 'sre' (expected: engineering, qa, product)", err)


if __name__ == "__main__":
    unittest.main()
