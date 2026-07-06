"""US0082/CR0179: mechanical digests of closed artefacts, drift-checked, originals preserved."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


digest = _load("digest")


def _bugs(root: Path) -> None:
    d = root / "sdlc-studio" / "bugs"; d.mkdir(parents=True)
    (d / "BG0001-closed.md").write_text(
        "# BG0001: a closed bug\n\n> **Status:** Closed\n> **Severity:** Low\n\n"
        "Relates to CR0042.\n", encoding="utf-8")
    (d / "BG0002-open.md").write_text(
        "# BG0002: still open\n\n> **Status:** Open\n> **Severity:** Low\n", encoding="utf-8")


class DigestTests(unittest.TestCase):
    def test_digests_only_closed_artefacts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _bugs(root)
            res = digest.build(root)
            self.assertEqual(res["count"], 1)  # only the Closed bug
            e = res["digests"][0]
            self.assertEqual(e["id"], "BG0001")
            self.assertIn("CR0042", e["refs"])

    def test_originals_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _bugs(root)
            before = (root / "sdlc-studio" / "bugs" / "BG0001-closed.md").read_text(encoding="utf-8")
            digest.build(root)
            after = (root / "sdlc-studio" / "bugs" / "BG0001-closed.md").read_text(encoding="utf-8")
            self.assertEqual(before, after)  # digest never rewrites the source

    def test_drift_detected_and_cleared(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _bugs(root)
            self.assertTrue(digest.is_stale(root))   # nothing written yet
            digest.main(["build", "--root", str(root)])
            self.assertFalse(digest.is_stale(root))  # fresh
            # close another bug -> the digest is now stale
            (root / "sdlc-studio" / "bugs" / "BG0002-open.md").write_text(
                "# BG0002: now closed\n\n> **Status:** Closed\n> **Severity:** Low\n", encoding="utf-8")
            self.assertTrue(digest.is_stale(root))


if __name__ == "__main__":
    unittest.main()
