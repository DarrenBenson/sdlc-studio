"""Unit tests for ac_scope.py - the cross-epic AC scope lint (CR0086)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ac_scope = _load("ac_scope")


def _epic(root: Path, disp: str, title: str) -> None:
    d = root / "sdlc-studio" / "epics"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{disp}-x.md").write_text(f"# {disp}: {title}\n\n> **Status:** Draft\n", encoding="utf-8")


def _story(root: Path, disp: str, epic: str, ac_body: str) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{disp}-x.md").write_text(
        f"# {disp}: s\n\n> **Status:** Draft\n> **Epic:** {epic}\n\n"
        f"## Acceptance Criteria\n\n{ac_body}\n", encoding="utf-8")


class AcScopeTests(unittest.TestCase):
    def test_flags_cross_epic_capability(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, "EP0001", "Platform & API Foundation")
            _epic(root, "EP0006", "Accounts & Cross-Device Sync")
            # an EP0001 story whose AC reaches into EP0006's "accounts" capability
            _story(root, "US0002", "EP0001",
                   "### AC1\n- **Then** a valid account token resolves a userId\n")
            findings = ac_scope.check(root)
            # the AC says "account" (singular); the title keyword is "accounts" - matched via root
            self.assertTrue(any(f["keyword"] == "accounts" and f["owner_epic"] == "EP0006"
                                for f in findings))

    def test_in_scope_story_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, "EP0001", "Platform & API Foundation")
            _epic(root, "EP0006", "Accounts & Cross-Device Sync")
            # an EP0006 story legitimately mentioning accounts - its own epic
            _story(root, "US0030", "EP0006",
                   "### AC1\n- **Then** the account is created\n")
            self.assertEqual(ac_scope.check(root), [])

    def test_shared_keyword_not_distinctive(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # "sync" appears in two epic titles -> not distinctive -> never flagged
            _epic(root, "EP0006", "Accounts & Sync")
            _epic(root, "EP0007", "Offline Sync Polish")
            _story(root, "US0001", "EP0001",
                   "### AC1\n- **Then** data will sync across devices\n")
            self.assertEqual([f for f in ac_scope.check(root) if f["keyword"] == "sync"], [])


if __name__ == "__main__":
    unittest.main()
