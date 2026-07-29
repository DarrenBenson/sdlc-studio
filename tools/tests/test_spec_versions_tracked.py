"""The specs' version is held against the product's (BG0310).

Both specs state "the document version tracks the product version" and nothing enforced it:
they sat at 4.1.0 after 5.0.0 was cut, `check_versions.py` never referenced them, and the
doc-freshness lane covers `LATEST.md` only. A rule the documents state about themselves and
no checker reads is a rule that is true until the day it matters.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _load():
    spec = importlib.util.spec_from_file_location("check_versions",
                                                  REPO / "tools" / "check_versions.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class SpecVersionsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load()

    def test_this_repos_specs_agree_with_the_product_version(self) -> None:
        found = {rel: self.mod.from_spec(REPO, rel) for rel in self.mod.SPEC_FILES}
        declared = {v for v in found.values() if v}
        self.assertTrue(declared, f"no spec declares a version at all: {found}")
        self.assertEqual({self.mod.from_skill_md(REPO)}, declared,
                         f"a spec's version disagrees with SKILL.md: {found}")

    def test_a_drifted_spec_is_reported(self) -> None:
        """The guard's own discrimination. Asserted against a fixture rather than this repo,
        so the check cannot pass merely because the tree happens to be tidy today."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / "trd.md").write_text("# TRD\n\n**Version:** 4.1.0\n",
                                                         encoding="utf-8")
            self.assertEqual("4.1.0", self.mod.from_spec(root, "sdlc-studio/trd.md"))

    def test_a_spec_declaring_no_version_is_not_a_home(self) -> None:
        """Absent is "not one of the homes", not a mismatch: a project whose specs carry no
        version must not be held to a rule it never adopted."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / "trd.md").write_text("# TRD\n\nno version here\n",
                                                         encoding="utf-8")
            self.assertIsNone(self.mod.from_spec(root, "sdlc-studio/trd.md"))

    def test_the_blockquoted_form_is_read_too(self) -> None:
        """The TSD writes `> **Version:**` and the TRD writes it plain. A reader that knew one
        spelling would silently exempt the other - the enumeration shape again."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / "tsd.md").write_text("# TSD\n\n> **Version:** 5.0.0\n",
                                                         encoding="utf-8")
            self.assertEqual("5.0.0", self.mod.from_spec(root, "sdlc-studio/tsd.md"))


if __name__ == "__main__":
    unittest.main()
