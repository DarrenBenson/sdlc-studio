"""US0060/CR0169: backfill structured raised_by onto artefacts, marking inferred, idempotent."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
from lib import sdlc_md  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


bf = _load("backfill_authorship")


def _bug(root: Path, name: str, meta: str) -> Path:
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{name}.md"
    p.write_text(f"# {name}: x\n\n> **Status:** Open\n> **Created-by:** sdlc-studio new\n{meta}\n",
                 encoding="utf-8")
    return p


class BackfillTests(unittest.TestCase):
    def test_backfills_and_marks_inferred(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, "BG0001-a", "> **Requester:** Sam Eriksson")
            res = bf.backfill(root, dry_run=False)
            self.assertEqual(res["backfilled"], 1)
            text = (root / "sdlc-studio" / "bugs" / "BG0001-a.md").read_text(encoding="utf-8")
            auth = sdlc_md.parse_authorship(text, "Raised-by")
            self.assertEqual(auth["name"], "Sam Eriksson")
            self.assertIn("inferred", text.lower())

    def test_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, "BG0001-a", "> **Requester:** Sam")
            bf.backfill(root, dry_run=False)
            second = bf.backfill(root, dry_run=False)
            self.assertEqual(second["backfilled"], 0)  # already has raised_by

    def test_plan_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = _bug(root, "BG0001-a", "> **Requester:** Sam")
            res = bf.backfill(root, dry_run=True)
            self.assertEqual(res["backfilled"], 1)
            self.assertIsNone(sdlc_md.parse_authorship(p.read_text(encoding="utf-8"), "Raised-by"))


if __name__ == "__main__":
    unittest.main()
